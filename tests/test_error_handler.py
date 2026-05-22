from unittest.mock import MagicMock

import aiohttp
import pytest
from fastapi import HTTPException

from app.utils.error_handler import handle_error_exception


@pytest.mark.parametrize(
    ("exc", "expected_status"),
    [
        (aiohttp.ClientConnectionError("down"), 503),
        (aiohttp.ServerTimeoutError("timeout"), 504),
        (ValueError("bad json"), 502),
        (RuntimeError("boom"), 500),
    ],
)
def test_handle_error_exception(exc: Exception, expected_status: int):
    result = handle_error_exception(exc, source="Test API")
    assert isinstance(result, HTTPException)
    assert result.status_code == expected_status
    assert "Test API" in result.detail


def test_handle_client_response_error_status():
    exc = aiohttp.ClientResponseError(
        request_info=MagicMock(),
        history=(),
        status=429,
        message="Too Many Requests",
    )
    result = handle_error_exception(exc, source="Steam")
    assert result.status_code == 429
