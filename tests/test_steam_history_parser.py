from datetime import datetime

from app.utils.steam_history_parser import parse_steam_listing_html

SSR_HTML = """
<html><body>
<script nonce="test-nonce">
window.SSR = {};
window.SSR.loaderData = ["{\\\"prices\\\":[{\\\"time\\\":1716508800,\\\"price_median\\\":14.97,\\\"purchases\\\":42},{\\\"time\\\":1716595200,\\\"price_median\\\":15.10,\\\"purchases\\\":30}]}];
</script>
</body></html>
"""

LINE1_HTML = """
<html><body>
<script nonce="legacy">
var line1=[["May 22 2026 12: +0", 14.97, "42"], ["May 23 2026 12: +0", 15.10, "30"]];
</script>
</body></html>
"""


def test_parse_ssr_prices_from_nonce_script():
    points = parse_steam_listing_html(SSR_HTML)

    assert len(points) == 2
    assert points[0].timestamp == datetime.fromtimestamp(1716508800)
    assert points[0].price == 14.97
    assert points[0].volume == 42.0
    assert points[1].price == 15.10


def test_parse_legacy_line1_from_nonce_script():
    points = parse_steam_listing_html(LINE1_HTML)

    assert len(points) == 2
    assert points[0].price == 14.97
    assert points[0].volume == 42.0
    assert points[1].price == 15.10


def test_parse_returns_empty_when_no_history():
    assert parse_steam_listing_html("<html><body>no data</body></html>") == []
