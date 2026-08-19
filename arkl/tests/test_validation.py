import pytest

from arkl.services.validation import (
    ARKLValidationError,
    validate_arkl_inputs,
)


def test_exposure_time_above_24_is_rejected():
    with pytest.raises(
        ARKLValidationError,
        match="exposure_time must be between 0 and 24",
    ):
        validate_arkl_inputs(
            concentration_ppm=10,
            body_weight=55,
            exposure_time=25,
            exposure_frequency=250,
            exposure_duration=10,
            inhalation_rate=0.83,
        )


def test_exposure_frequency_above_365_is_rejected():
    with pytest.raises(
        ARKLValidationError,
        match="exposure_frequency must be between 0 and 365",
    ):
        validate_arkl_inputs(
            concentration_ppm=10,
            body_weight=55,
            exposure_time=8,
            exposure_frequency=366,
            exposure_duration=10,
            inhalation_rate=0.83,
        )


def test_zero_exposure_duration_is_rejected():
    with pytest.raises(
        ARKLValidationError,
        match="exposure_duration must be greater than zero",
    ):
        validate_arkl_inputs(
            concentration_ppm=10,
            body_weight=55,
            exposure_time=8,
            exposure_frequency=250,
            exposure_duration=0,
            inhalation_rate=0.83,
        )
