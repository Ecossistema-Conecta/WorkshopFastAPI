from fastapi.responses import JSONResponse
from http import HTTPStatus

from src.exceptions.types import ConflictError

errors = (ConflictError,)

async def global_exception_handler(error: Exception) -> JSONResponse:
    if isinstance(error, errors):
        return JSONResponse(
            status_code=error.status_code,
            content={
                "errors": [
                    {
                        "title": getattr(error, "name", error.__class__.__name__),
                        "detail": getattr(error, "message", str(error)),
                    }
                ]
            }
        )

    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={
            "errors": [
                {
                    "title": "InternalServerError",
                    "detail": str(error),
                }
            ]
        }
    )
