from datetime import date
from typing import TypedDict
from app.core.dates import parse_date
from app.core.money import round_half_up


class QuoteResult(TypedDict):
    listing_id: int
    check_in: str
    check_out: str
    nights: int
    nightly_cents: int
    subtotal_cents: int
    cleaning_cents: int
    service_cents: int
    total_cents: int
    currency: str


def calculate_quote(
    listing_id: int,
    check_in: date | str,
    check_out: date | str,
    nightly_price_cents: int,
    cleaning_fee_cents: int = 0,
) -> QuoteResult:
    """
    Authoritative pricing calculation per PRD §10.2:
    nights    = check_out - check_in
    subtotal  = price_cents * nights
    cleaning  = cleaning_fee_cents
    service   = round_half_up(subtotal * 0.12)
    total     = subtotal + cleaning + service
    """
    d_in = parse_date(check_in) if isinstance(check_in, str) else check_in
    d_out = parse_date(check_out) if isinstance(check_out, str) else check_out

    if d_out <= d_in:
        raise ValueError("check_out must be strictly after check_in")

    nights = (d_out - d_in).days
    subtotal_cents = nightly_price_cents * nights
    cleaning_cents = cleaning_fee_cents
    service_cents = round_half_up(subtotal_cents * 0.12)
    total_cents = subtotal_cents + cleaning_cents + service_cents

    return {
        "listing_id": listing_id,
        "check_in": d_in.strftime("%Y-%m-%d"),
        "check_out": d_out.strftime("%Y-%m-%d"),
        "nights": nights,
        "nightly_cents": nightly_price_cents,
        "subtotal_cents": subtotal_cents,
        "cleaning_cents": cleaning_cents,
        "service_cents": service_cents,
        "total_cents": total_cents,
        "currency": "USD",
    }
