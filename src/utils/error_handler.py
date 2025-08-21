import aiohttp
from fastapi import HTTPException

def handle_error_exception(e: Exception, source: str) -> HTTPException:
    if isinstance(e, aiohttp.ClientConnectionError):
        return HTTPException(status_code=503, detail=f"Network error fetching price from {source}: {str(e)}")

    if isinstance(e, aiohttp.ClientResponseError):
        status_code = e.status if hasattr(e, 'status') else 502
        return HTTPException(status_code=status_code, detail=f"{source} HTTP error: {str(e)}")

    if isinstance(e, aiohttp.ClientTimeout):
        return HTTPException(status_code=504, detail=f"Timeout while fetching from {source}: {str(e)}")

    if isinstance(e, ValueError):
        return HTTPException(status_code=502, detail=f"Failed to parse {source} response: {str(e)}")

    return HTTPException(status_code=500, detail=f"Unexpected error while processing {source}: {str(e)}")