import json
import re
from datetime import datetime

from app.schemas.history_responses import HistoryPoint

_LINE1_PATTERN = re.compile(r"var\s+line1\s*=\s*(\[\[.+?\]\]);", re.DOTALL)
_SSR_PRICE_POINT_PATTERN = re.compile(
    r'time\\+":(\d+),\\+"price_median\\+":([\d.eE+-]+),\\+"purchases\\+":(\d+)'
)
_SCRIPT_BODY_PATTERN = re.compile(
    r"<script\b[^>]*>(.*?)</script>",
    re.DOTALL | re.IGNORECASE,
)
_NONCE_SCRIPT_BODY_PATTERN = re.compile(
    r'<script\b[^>]*\bnonce="[^"]*"[^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)


def parse_steam_listing_html(html: str) -> list[HistoryPoint]:
    script_bodies = _NONCE_SCRIPT_BODY_PATTERN.findall(html)
    if not script_bodies:
        script_bodies = _SCRIPT_BODY_PATTERN.findall(html)

    for body in sorted(script_bodies, key=len, reverse=True):
        points = _parse_script_body(body)
        if points:
            return points

    points = _parse_script_body(html)
    if points:
        return points

    return []


def _parse_script_body(body: str) -> list[HistoryPoint]:
    line1_match = _LINE1_PATTERN.search(body)
    if line1_match:
        try:
            raw_points = json.loads(line1_match.group(1))
        except json.JSONDecodeError:
            raw_points = []
        points = [_line1_entry_to_point(entry) for entry in raw_points]
        return [point for point in points if point is not None]

    ssr_points = _parse_ssr_price_points(body)
    if ssr_points:
        return ssr_points

    return []


def _parse_ssr_price_points(body: str) -> list[HistoryPoint]:
    points: list[HistoryPoint] = []
    seen_times: set[int] = set()

    for time_raw, price_raw, volume_raw in _SSR_PRICE_POINT_PATTERN.findall(body):
        ts = int(time_raw)
        if ts in seen_times:
            continue
        seen_times.add(ts)
        points.append(
            HistoryPoint(
                timestamp=datetime.fromtimestamp(ts),
                price=round(float(price_raw), 4),
                volume=float(volume_raw),
            )
        )

    points.sort(key=lambda point: point.timestamp)
    return points


def _line1_entry_to_point(entry: list) -> HistoryPoint | None:
    if not entry or len(entry) < 2:
        return None

    date_str = str(entry[0])
    price_raw = entry[1]
    volume_raw = entry[2] if len(entry) > 2 else None

    try:
        price = float(price_raw)
    except (TypeError, ValueError):
        return None

    timestamp = _parse_line1_date(date_str)
    if timestamp is None:
        return None

    volume: float | None = None
    if volume_raw is not None:
        try:
            volume = float(volume_raw)
        except (TypeError, ValueError):
            volume = None

    return HistoryPoint(
        timestamp=timestamp,
        price=round(price, 4),
        volume=volume,
    )


def _parse_line1_date(date_str: str) -> datetime | None:
    cleaned = re.sub(r"\s*:\s*\+?\d+$", "", date_str.strip())
    for fmt in ("%b %d %Y %H", "%b %d %Y %H:%M"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None
