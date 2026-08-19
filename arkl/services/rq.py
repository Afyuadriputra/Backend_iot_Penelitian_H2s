from decimal import Decimal

from arkl.services.constants import H2S_RFC_MG_M3
from arkl.services.validation import (
    ARKLValidationError,
    to_decimal,
)


def calculate_rq(
    *,
    exposure_concentration_mg_m3,
    rfc=H2S_RFC_MG_M3,
) -> Decimal:
    exposure_concentration = to_decimal(
        exposure_concentration_mg_m3,
        "exposure_concentration_mg_m3",
    )

    reference_concentration = to_decimal(
        rfc,
        "rfc",
    )

    if exposure_concentration < 0:
        raise ARKLValidationError("exposure_concentration_mg_m3 cannot be negative.")

    if reference_concentration <= 0:
        raise ARKLValidationError("rfc must be greater than zero.")

    return exposure_concentration / reference_concentration
