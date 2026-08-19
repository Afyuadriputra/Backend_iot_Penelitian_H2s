from dataclasses import dataclass


class ExposureValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ExposureData:
    body_weight: float
    exposure_time: float
    exposure_frequency: float
    exposure_duration: float
    inhalation_rate: float


def validate_exposure_data(
    *,
    body_weight: float,
    exposure_time: float,
    exposure_frequency: float,
    exposure_duration: float,
    inhalation_rate: float,
) -> ExposureData:
    values = {
        "body_weight": body_weight,
        "exposure_time": exposure_time,
        "exposure_frequency": exposure_frequency,
        "exposure_duration": exposure_duration,
        "inhalation_rate": inhalation_rate,
    }

    for name, value in values.items():
        if not isinstance(value, (int, float)):
            raise ExposureValidationError(f"{name} must be numeric.")

    if body_weight <= 0:
        raise ExposureValidationError("body_weight must be greater than zero.")

    if exposure_time < 0:
        raise ExposureValidationError("exposure_time cannot be negative.")

    if exposure_frequency < 0:
        raise ExposureValidationError("exposure_frequency cannot be negative.")

    if exposure_duration < 0:
        raise ExposureValidationError("exposure_duration cannot be negative.")

    if inhalation_rate < 0:
        raise ExposureValidationError("inhalation_rate cannot be negative.")

    return ExposureData(
        body_weight=float(body_weight),
        exposure_time=float(exposure_time),
        exposure_frequency=float(exposure_frequency),
        exposure_duration=float(exposure_duration),
        inhalation_rate=float(inhalation_rate),
    )
