from decimal import Decimal, ROUND_HALF_UP


def round_half_up(value: float | Decimal) -> int:
    """Half-up rounding for cents calculation."""
    d = Decimal(str(value))
    return int(d.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def format_cents_to_dollars(cents: int) -> str:
    """Format integer cents to dollars string (e.g. 14200 -> '$142', 14250 -> '$142.50')."""
    dollars = Decimal(cents) / Decimal(100)
    if cents % 100 == 0:
        return f"${int(dollars)}"
    return f"${dollars:.2f}"
