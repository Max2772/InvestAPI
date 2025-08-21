import httpx
from fastapi import HTTPException

def handle_error_exception(e: Exception, source: str) -> HTTPException:
    if isinstance(e, httpx.RequestError):
        return HTTPException(status_code=503, detail=f"Network error fetching price from {source}: {str(e)}")

    if isinstance(e, httpx.HTTPStatusError):
        status_code = e.response.status_code if e.response else 502
        return HTTPException(status_code=status_code, detail=f"{source} HTTP error: {str(e)}")

    if isinstance(e, ValueError):
        return HTTPException(status_code=502, detail=f"Failed to parse {source} response: {str(e)}")

    return HTTPException(status_code=500, detail=f"Unexpected error while processing {source}: {str(e)}")