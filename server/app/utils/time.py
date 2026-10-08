from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


UTC = timezone.utc
LAGOS = ZoneInfo("Africa/Lagos")


def now_utc() -> datetime:
    return datetime.now(UTC)


def current_lagos_date() -> datetime.date:
    return now_utc().astimezone(LAGOS).date()


def utc_bounds_for_lagos_date(local_date):
    """Return the UTC half-open range for one Africa/Lagos calendar day."""
    start_local = datetime.combine(local_date, time.min, tzinfo=LAGOS)
    end_local = start_local + timedelta(days=1)
    return start_local.astimezone(UTC), end_local.astimezone(UTC)


def ensure_utc(value: datetime) -> datetime:
    """Normalize a datetime to an aware UTC datetime."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def is_future(value: datetime, *, reference: datetime | None = None) -> bool:
    return ensure_utc(value) > (reference or now_utc())
