from datetime import date, datetime, time, timedelta, timezone


def days_between_iso_utc(start: date, end: date, *, inclusive: bool = True) -> list[str]:
    if start > end:
        start, end = end, start

    delta_days = (end - start).days
    n = delta_days + 1 if inclusive else delta_days

    out: list[str] = []
    for i in range(n):
        d = start + timedelta(days=i)
        dt_utc = datetime.combine(d, time.min, tzinfo=timezone.utc)  # 00:00:00 UTC
        out.append(dt_utc.isoformat())
    return out
