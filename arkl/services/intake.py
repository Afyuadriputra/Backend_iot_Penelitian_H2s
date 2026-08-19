from decimal import Decimal

from arkl.services.constants import DAYS_PER_YEAR
from arkl.services.validation import ARKLValidationError, to_decimal


def calculate_averaging_time(
    exposure_duration_year,
) -> Decimal:
    duration = to_decimal(
        exposure_duration_year,
        "exposure_duration_year",
    )

    if duration <= 0:
        raise ARKLValidationError("exposure_duration_year must be greater than zero.")

    return duration * DAYS_PER_YEAR


def calculate_intake(
    *,
    concentration_mg_m3,
    inhalation_rate_m3_hour,
    exposure_time_hour_day,
    exposure_frequency_day_year,
    exposure_duration_year,
    body_weight_kg,
) -> Decimal:
    concentration = to_decimal(
        concentration_mg_m3,
        "concentration_mg_m3",
    )
    inhalation_rate = to_decimal(
        inhalation_rate_m3_hour,
        "inhalation_rate_m3_hour",
    )
    exposure_time = to_decimal(
        exposure_time_hour_day,
        "exposure_time_hour_day",
    )
    exposure_frequency = to_decimal(
        exposure_frequency_day_year,
        "exposure_frequency_day_year",
    )
    exposure_duration = to_decimal(
        exposure_duration_year,
        "exposure_duration_year",
    )
    body_weight = to_decimal(
        body_weight_kg,
        "body_weight_kg",
    )

    if concentration < 0:
        raise ARKLValidationError("concentration_mg_m3 cannot be negative.")

    if inhalation_rate < 0:
        raise ARKLValidationError("inhalation_rate_m3_hour cannot be negative.")

    if not Decimal("0") <= exposure_time <= Decimal("24"):
        raise ARKLValidationError("exposure_time_hour_day must be between 0 and 24.")

    if not Decimal("0") <= exposure_frequency <= Decimal("365"):
        raise ARKLValidationError(
            "exposure_frequency_day_year must be between 0 and 365."
        )

    if exposure_duration <= 0:
        raise ARKLValidationError("exposure_duration_year must be greater than zero.")

    if body_weight <= 0:
        raise ARKLValidationError("body_weight_kg must be greater than zero.")

    averaging_time = calculate_averaging_time(exposure_duration)

    numerator = (
        concentration
        * inhalation_rate
        * exposure_time
        * exposure_frequency
        * exposure_duration
    )

    denominator = body_weight * averaging_time

    return numerator / denominator
