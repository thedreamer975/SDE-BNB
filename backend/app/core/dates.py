from datetime import date, datetime, timezone
from typing import Callable

_custom_today_fn: Callable[[], str] | None = None


def get_server_today() -> str:
    """Returns today's date in YYYY-MM-DD UTC format, supporting test overrides."""
    if _custom_today_fn is not None:
        return _custom_today_fn()
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def set_custom_today(fn: Callable[[], str] | None) -> None:
    """Inject a custom date function for deterministic testing."""
    global _custom_today_fn
    _custom_today_fn = fn


def parse_date(date_str: str) -> date:
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def format_date(d: date) -> str:
    return d.strftime("%Y-%m-%d")
