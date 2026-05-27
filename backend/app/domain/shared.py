from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal

MONEY_QUANTUM = Decimal("0.01")


def normalize_money(amount: Decimal) -> Decimal:
    return amount.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


def utc_now() -> datetime:
    return datetime.now(UTC)


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        msg = "Timestamps must be timezone-aware UTC values."
        raise ValueError(msg)

    return value.astimezone(UTC)
