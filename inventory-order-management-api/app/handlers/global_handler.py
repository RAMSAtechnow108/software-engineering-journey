from fastapi import Request
from fastapi.responses import JSONResponse
import logging


logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unexpected error occurred")
    return JSONResponse(
        status_code=500,
        content = {
            "success": False,
            "message": "Internal Server Error",
            "error_code": "INTERNAL_SERVER_ERROR"
        },
    )
    