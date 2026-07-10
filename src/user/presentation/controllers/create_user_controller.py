from typing import Annotated, Any

from fastapi import Depends

from src.common.presentation.helpers import created
from src.common.presentation.http_types import HttpRequest, HttpResponse
from src.common.presentation.interfaces import IController
from src.user.application.use_case.user import CreateUserUseCase, SendNewUserEmailUseCase
from src.user.domain.models import CreateUserModel
from src.user.domain.use_case.user import ICreateUserUseCase, ISendNewUserEmailUseCase


class CreateUserController(IController):
    def __init__(
            self,
            create_user_use_case: Annotated[ICreateUserUseCase, Depends(CreateUserUseCase)],
            send_new_user_email_use_case: Annotated[ISendNewUserEmailUseCase, Depends(SendNewUserEmailUseCase)]
        ):
        self.__create_user_use_case = create_user_use_case
        self.__send_new_user_email_use_case = send_new_user_email_use_case

    async def handle(self, http_request: HttpRequest) -> HttpResponse:
        body: Any = http_request.body
        new_user = CreateUserModel(**body)

        temp_password, created_user = await self.__create_user_use_case.execute(user=new_user)
        await self.__send_new_user_email_use_case.execute(temp_password=temp_password, user=created_user)

        return created()
