from decimal import Decimal

from arkl.services.intake import (
    calculate_averaging_time,
    calculate_intake,
)


def test_averaging_time():
    result = calculate_averaging_time(Decimal("10"))

    assert result == Decimal("3650")


def test_known_intake_calculation():
    result = calculate_intake(
        concentration_mg_m3=Decimal("14"),
        inhalation_rate_m3_hour=Decimal("0.83"),
        exposure_time_hour_day=Decimal("8"),
        exposure_frequency_day_year=Decimal("250"),
        exposure_duration_year=Decimal("10"),
        body_weight_kg=Decimal("55"),
    )

    expected = (
        Decimal("14") * Decimal("0.83") * Decimal("8") * Decimal("250") * Decimal("10")
    ) / (Decimal("55") * Decimal("3650"))

    assert result == expected


def test_intake_is_deterministic():
    kwargs = {
        "concentration_mg_m3": Decimal("14"),
        "inhalation_rate_m3_hour": Decimal("0.83"),
        "exposure_time_hour_day": Decimal("8"),
        "exposure_frequency_day_year": Decimal("250"),
        "exposure_duration_year": Decimal("10"),
        "body_weight_kg": Decimal("55"),
    }

    first = calculate_intake(**kwargs)
    second = calculate_intake(**kwargs)

    assert first == second


def test_zero_concentration_produces_zero_intake():
    result = calculate_intake(
        concentration_mg_m3=0,
        inhalation_rate_m3_hour="0.83",
        exposure_time_hour_day=8,
        exposure_frequency_day_year=250,
        exposure_duration_year=10,
        body_weight_kg=55,
    )

    assert result == Decimal("0")
