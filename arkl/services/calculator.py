from django.db import transaction

from arkl.models import ARKLResult
from arkl.services.aggregation import calculate_mean_concentration
from arkl.services.constants import (
    ARKL_CALCULATION_VERSION,
    H2S_RFC,
)
from arkl.services.conversion import ppm_to_mg_m3
from arkl.services.intake import (
    calculate_averaging_time,
    calculate_intake,
)
from arkl.services.interpretation import interpret_rq
from arkl.services.rq import calculate_rq
from arkl.services.validation import (
    ARKLValidationError,
    validate_arkl_inputs,
)
from devices.models import Device, H2SReading
from exposure.models import ExposureProfile, Worker


class ARKLCalculationError(ValueError):
    pass


def _get_exposure_profile(
    worker: Worker,
) -> ExposureProfile:
    try:
        return worker.exposure_profile
    except ExposureProfile.DoesNotExist as exc:
        raise ARKLCalculationError(
            "Worker does not have an exposure profile."
        ) from exc


def _validate_active_device(
    device: Device,
) -> None:
    if not device.is_active:
        raise ARKLCalculationError(
            "Device is inactive."
        )


def _get_latest_reading(
    device: Device,
) -> H2SReading:
    reading = (
        H2SReading.objects.filter(
            device=device,
        )
        .order_by(
            "-received_at",
            "-id",
        )
        .first()
    )

    if reading is None:
        raise ARKLCalculationError(
            "No H2S reading available for this device."
        )

    return reading


def _calculate_values(
    *,
    concentration_ppm,
    exposure_profile: ExposureProfile,
) -> dict:
    """
    Calculate ARKL inhalation risk.

    Pipeline:

        ppm
        ↓
        concentration mg/m3
        ↓
        averaging time
        ↓
        intake
        ↓
        RQ
        ↓
        interpretation

    Formula:

        I = (C × R × tE × fE × Dt)
            -----------------------
                  Wb × tavg

        RQ = I / RfC
    """

    validated = validate_arkl_inputs(
        concentration_ppm=concentration_ppm,
        body_weight=exposure_profile.body_weight,
        exposure_time=exposure_profile.exposure_time,
        exposure_frequency=(
            exposure_profile.exposure_frequency
        ),
        exposure_duration=(
            exposure_profile.exposure_duration
        ),
        inhalation_rate=(
            exposure_profile.inhalation_rate
        ),
    )

    # STEP 1
    # Convert sensor concentration:
    #
    # ppm → mg/m3
    concentration_mg_m3 = ppm_to_mg_m3(
        validated.concentration_ppm
    )

    # STEP 2
    # Non-carcinogenic averaging time:
    #
    # tavg = Dt × 365
    averaging_time = calculate_averaging_time(
        validated.exposure_duration_year
    )

    # STEP 3
    # Calculate inhalation intake:
    #
    # I =
    # C × R × tE × fE × Dt
    # ---------------------
    # Wb × tavg
    intake = calculate_intake(
        concentration_mg_m3=(
            concentration_mg_m3
        ),
        inhalation_rate_m3_hour=(
            validated.inhalation_rate_m3_hour
        ),
        exposure_time_hour_day=(
            validated.exposure_time_hour_day
        ),
        exposure_frequency_day_year=(
            validated.exposure_frequency_day_year
        ),
        exposure_duration_year=(
            validated.exposure_duration_year
        ),
        body_weight_kg=(
            validated.body_weight_kg
        ),
        averaging_time_day=averaging_time,
    )

    # STEP 4
    # Risk Quotient:
    #
    # RQ = Intake / RfC
    rq = calculate_rq(
        intake=intake,
        rfc=H2S_RFC,
    )

    # STEP 5
    # Interpret:
    #
    # RQ <= 1 -> WITHIN_REFERENCE_LEVEL
    # RQ > 1  -> ABOVE_REFERENCE_LEVEL
    interpretation = interpret_rq(rq)

    return {
        "concentration_ppm": (
            validated.concentration_ppm
        ),
        "concentration_mg_m3": (
            concentration_mg_m3
        ),

        # No longer the primary ARKL v2 calculation.
        # Kept nullable for historical compatibility.
        "exposure_concentration_mg_m3": None,

        # Exposure profile snapshots.
        "body_weight": (
            validated.body_weight_kg
        ),
        "exposure_time": (
            validated.exposure_time_hour_day
        ),
        "exposure_frequency": (
            validated.exposure_frequency_day_year
        ),
        "exposure_duration": (
            validated.exposure_duration_year
        ),
        "inhalation_rate": (
            validated.inhalation_rate_m3_hour
        ),

        # ARKL v2 calculation outputs.
        "averaging_time": averaging_time,
        "intake": intake,
        "rfc": H2S_RFC,
        "rq": rq,
        "interpretation": interpretation,
    }


@transaction.atomic
def calculate_realtime_risk(
    *,
    worker: Worker,
    device: Device,
) -> ARKLResult:
    _validate_active_device(device)

    exposure_profile = _get_exposure_profile(worker)
    reading = _get_latest_reading(device)

    try:
        values = _calculate_values(
            concentration_ppm=reading.ppm,
            exposure_profile=exposure_profile,
        )
    except ARKLValidationError as exc:
        raise ARKLCalculationError(
            str(exc)
        ) from exc

    return ARKLResult.objects.create(
        worker=worker,
        reading=reading,
        calculation_type=(
            ARKLResult.CalculationType.REALTIME
        ),
        calculation_version=(
            ARKL_CALCULATION_VERSION
        ),
        source_simulated=reading.simulated,
        **values,
    )


@transaction.atomic
def calculate_historical_risk(
    *,
    worker: Worker,
    device: Device,
    period_start,
    period_end,
) -> ARKLResult:
    if period_start >= period_end:
        raise ARKLCalculationError(
            "period_start must be earlier than period_end."
        )

    _validate_active_device(device)

    exposure_profile = _get_exposure_profile(worker)

    readings = list(
        H2SReading.objects.filter(
            device=device,
            received_at__gte=period_start,
            received_at__lte=period_end,
        ).order_by(
            "received_at",
            "id",
        )
    )

    if not readings:
        raise ARKLCalculationError(
            "No H2S readings available in the selected period."
        )

    # Historical ARKL uses arithmetic mean
    # of H2S concentration during selected period.
    mean_ppm = calculate_mean_concentration(
        [
            reading.ppm
            for reading in readings
        ]
    )

    try:
        values = _calculate_values(
            concentration_ppm=mean_ppm,
            exposure_profile=exposure_profile,
        )
    except ARKLValidationError as exc:
        raise ARKLCalculationError(
            str(exc)
        ) from exc

    return ARKLResult.objects.create(
        worker=worker,
        reading=None,
        calculation_type=(
            ARKLResult.CalculationType.HISTORICAL
        ),
        calculation_version=(
            ARKL_CALCULATION_VERSION
        ),
        source_simulated=any(
            reading.simulated
            for reading in readings
        ),
        period_start=period_start,
        period_end=period_end,
        reading_count=len(readings),
        **values,
    )