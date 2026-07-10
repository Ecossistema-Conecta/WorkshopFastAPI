from http import HTTPStatus

from fastapi import Depends, APIRouter

from src.exceptions import global_exception_handler
from src.main.adapters import request_adapter
from fastapi import Request
from src.main.schemas.user import CreateUserSchema
from src.user.presentation.controllers import CreateUserController


router = APIRouter()

@router.post('/user/', status_code=HTTPStatus.CREATED, tags=['users'])
async def create_user(user: CreateUserSchema, request: Request, controller: CreateUserController = Depends()):
    try:
        http_response = await request_adapter(request=request, controller_handler=controller.handle, parsed_body=user.model_dump())
    except Exception as exception:  # pylint: disable=broad-except
        print(exception)
        http_response = await global_exception_handler(exception)

    return http_response
