from datetime import date, datetime, timedelta

from app.schemas.history_responses import DAILY_INTERVAL, HistoryPoint

__all__ = ["DAILY_INTERVAL", "HistoryPoint", "filter_points_by_days", "collapse_to_daily"]


def filter_points_by_days(points: list[HistoryPoint], days: int) -> list[HistoryPoint]:
    cutoff = datetime.now() - timedelta(days=days)
    return [point for point in points if point.timestamp >= cutoff]


def collapse_to_daily(points: list[HistoryPoint]) -> list[HistoryPoint]:
    if not points:
        return []

    daily_last: dict[date, HistoryPoint] = {}
    daily_volume: dict[date, float] = {}

    for point in sorted(points, key=lambda item: item.timestamp):
        day = point.timestamp.date()
        if point.volume is not None:
            daily_volume[day] = daily_volume.get(day, 0.0) + point.volume
        daily_last[day] = point

    result: list[HistoryPoint] = []
    for day in sorted(daily_last.keys()):
        source = daily_last[day]
        result.append(
            HistoryPoint(
                timestamp=datetime.combine(day, datetime.min.time()),
                price=source.price,
                volume=round(daily_volume[day], 4) if day in daily_volume else source.volume,
            )
        )
    return result
