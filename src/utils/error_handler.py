import httpx
from fastapi import HTTPException

def handle_error_exception(e: Exception, source: str) -> HTTPException:
    if isinstance(e, httpx.NetworkError):
        return HTTPException(status_code=503, detail=f"Network error fetching price from {source}: {str(e)}")

    if isinstance(e, httpx.HTTPStatusError):
        status_code = e.response.status_code if e.response.status_code else 502
        return HTTPException(status_code=status_code, detail=f"{source} HTTP error: {str(e)}")

    return HTTPException(status_code=500, detail=f"Error parsing {source} response: {str(e)}")