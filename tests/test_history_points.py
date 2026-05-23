from datetime import datetime

from app.schemas.history_responses import HistoryPoint
from app.utils.history_points import collapse_to_daily, filter_points_by_days


def test_collapse_to_daily_keeps_last_price_per_day():
    points = [
        HistoryPoint(timestamp=datetime(2026, 5, 1, 10, 0), price=10.0, volume=1.0),
        HistoryPoint(timestamp=datetime(2026, 5, 1, 18, 0), price=12.0, volume=2.0),
        HistoryPoint(timestamp=datetime(2026, 5, 2, 9, 0), price=11.0, volume=3.0),
    ]

    daily = collapse_to_daily(points)

    assert len(daily) == 2
    assert daily[0].timestamp == datetime(2026, 5, 1)
    assert daily[0].price == 12.0
    assert daily[0].volume == 3.0
    assert daily[1].price == 11.0


def test_filter_points_by_days():
    now = datetime.now()
    points = [
        HistoryPoint(timestamp=now.replace(year=now.year - 1), price=1.0),
        HistoryPoint(timestamp=now, price=2.0),
    ]

    filtered = filter_points_by_days(points, 30)

    assert len(filtered) == 1
    assert filtered[0].price == 2.0
