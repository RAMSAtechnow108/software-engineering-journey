from fastapi.responses import JSONResponse
from fastapi import Request
from app.exceptions.product_exceptions import AppException


async def app_exception_handler(request:Request, exc: AppException):
    return JSONResponse(
        status_code =exc.status_code,
        
        content = {
            "success":False,
            "message": exc.message,
            "error_code": exc.error_code
        }
    )


