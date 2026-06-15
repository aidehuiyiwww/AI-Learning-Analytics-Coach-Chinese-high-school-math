from datetime import datetime
from math import exp

LEARNING_RATE = 0.08


def clamp(x, low=0.0, high=1.0):
    return max(low, min(high, x))


def update_mastery_score(old_mastery, difficulty, is_correct):
    difficulty_weight = max(1, min(5, int(difficulty))) / 3.0
    outcome = 1 if is_correct else -1
    return clamp(float(old_mastery) + LEARNING_RATE * difficulty_weight * outcome)


def parse_datetime_safe(value):
    """Return datetime or None. Robust to None, empty strings, NaN, pandas Timestamp, and ISO strings."""
    if value is None:
        return None
    try:
        if value != value:  # NaN / NaT
            return None
    except Exception:
        pass
    if isinstance(value, datetime):
        return value
    if hasattr(value, "to_pydatetime"):
        try:
            return value.to_pydatetime()
        except Exception:
            pass
    value = str(value).strip()
    if not value or value.lower() in {"none", "nan", "nat", "never"}:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        try:
            # Handles values such as '2026-06-15 12:30:00'
            return datetime.strptime(value[:19], "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None


def adjusted_mastery(raw_mastery, last_practiced):
    last = parse_datetime_safe(last_practiced)
    if last is None:
        return clamp(float(raw_mastery) * 0.8)
    days = max(0, (datetime.now() - last).days)
    return clamp(float(raw_mastery) * exp(-days / 30.0))


def days_since_practice(last_practiced, never_days=999):
    last = parse_datetime_safe(last_practiced)
    if last is None:
        return never_days
    return max(0, (datetime.now() - last).days)
