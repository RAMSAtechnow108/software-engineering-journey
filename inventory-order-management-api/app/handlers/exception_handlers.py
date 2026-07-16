from fastapi.responses import JSONResponse
from fastapi import status,Request
from app.exceptions.product_exceptions import ProductNotFoundError




async def product_not_found_handler(request: Request,exc:ProductNotFoundError):

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content = {
            "message":str(exc)
        }
    )