from http import HTTPStatus

from src.exceptions.types.api_error import ApiError


class ConflictError(ApiError):
    status_code = HTTPStatus.CONFLICT  # pyright: ignore[reportUnannotatedClassAttribute]

    def __init__(self, message: str = 'Entity already exists'):
        super().__init__(message, name='ConflictError')
