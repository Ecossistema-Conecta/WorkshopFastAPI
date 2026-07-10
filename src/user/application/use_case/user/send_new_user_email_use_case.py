import math
from datetime import datetime, time, timedelta
from http import HTTPStatus
from random import randint
from typing import Annotated

from fastapi import Depends

from src.common.application.interfaces.adapters import IMailerAdapter
from src.common.application.interfaces.repository import IEmailLogRepository, IRedisRepository
from src.common.domain.models import EmailCacheKeys, MailerAdapterResponse
from src.common.infra.adapters import MailerAdapter
from src.common.infra.repositories import EmailLogRepository, RedisRepository
from src.main.config import settings
from src.user.domain.models import EmailLogResponseModel, UserModel
from src.user.domain.use_case.user import ISendNewUserEmailUseCase


class SendNewUserEmailUseCase(ISendNewUserEmailUseCase):
    def __init__(
        self,
        email_log_repository: Annotated[IEmailLogRepository, Depends(EmailLogRepository)],
        mailer_adapter: Annotated[IMailerAdapter, Depends(MailerAdapter)],
        redis_repository: Annotated[IRedisRepository, Depends(RedisRepository)]
    ) -> None:
        self.__email_log_repository = email_log_repository
        self.__mailer_adapter = mailer_adapter
        self.__redis_repository = redis_repository

    async def execute(self, temp_password: str, user: UserModel) -> EmailLogResponseModel:
        key = EmailCacheKeys.EMAIL_RATE_LIMIT_QUOTA.value
        rate_limit_count = await self.__redis_repository.get(key=key)
        in_seconds = await self.calc_expires()

        if rate_limit_count == 0:
            retry_after = in_seconds + randint(1, 700)

            await self.__redis_repository.insert_expires(key=key, value=0, expires_in=in_seconds)

            return EmailLogResponseModel(
                success=False,
                status_code=HTTPStatus.TOO_MANY_REQUESTS,
                error_message='Rate limit exceeded',
                retry_after=retry_after,
            )

        response, subject, body = await self.send_new_user_email(temp_password=temp_password, new_user=user)
        status_code = response.status_code
        email_id = response.email_id
        remaining_quota = response.rate_limit_remaining

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS and response.retry_after:
            retry_after = response.retry_after + randint(1, 700)

            await self.__redis_repository.insert_expires(key=key, value=remaining_quota, expires_in=in_seconds)
            log_id = await self.__email_log_repository.create_send_new_user_email_log(
                id_control=email_id, receiver_id=user.id, sender_id=None, subject=subject, body=body, error='Rate limit exceeded'
            )

            return EmailLogResponseModel(
                success=False,
                log_id=log_id,
                status_code=status_code,
                error_message='Rate limit exceeded',
                retry_after=retry_after,
            )

        if not response.success:
            log_id = await self.__email_log_repository.create_send_new_user_email_log(
                id_control=email_id, receiver_id=user.id, sender_id=None, subject=subject, body=body, error=response.error_message
            )

            return EmailLogResponseModel(
                success=False, log_id=log_id, status_code=status_code, error_message=response.error_message
            )

        await self.__redis_repository.insert_expires(key=key, value=remaining_quota, expires_in=in_seconds)
        log_id = await self.__email_log_repository.create_send_new_user_email_log(
            id_control=email_id, receiver_id=user.id, sender_id=None, subject=subject, body=body, error=None
        )

        return EmailLogResponseModel(success=True, log_id=log_id, status_code=status_code)

    async def send_new_user_email(self, temp_password: str, new_user: UserModel) -> tuple[MailerAdapterResponse, str, str]:
        receiver = new_user.email
        user_name = new_user.name
        body = await self.get_first_access_email(temp_password=temp_password)
        subject = str('Bem vindo(a) ao Projeto')

        response = await self.__mailer_adapter.send_email(
            sender_email=settings.DEFAULT_EMAIL,
            sender_name=settings.PROJECT_NAME,
            receiver_email=receiver,
            receiver_name=user_name,
            subject=subject,
            content=body,
        )

        return response, subject, body

    @staticmethod
    async def calc_expires() -> int:
        now = datetime.now()
        reset_time = now + timedelta(days=1)
        reset_time = datetime.combine(reset_time.date(), time(0, 0, 0))
        diff = reset_time - now
        return math.ceil(diff.total_seconds())

    @staticmethod
    async def get_first_access_email(temp_password: str) -> str:
        return f'''<h3>Prezado(a) usuário(a),</h3>
        Siga os passos abaixo para fazer seu primeiro acesso ao sistema:</p>
        <ol>
          <li>Faça login utilizando a senha temporária fornecida abaixo.</li>
          <li>Você será automaticamente redirecionado para uma página segura, onde poderá criar uma nova senha pessoal.</li>
          <li>Insira e confirme sua nova senha e, em seguida, clique em "Salvar" para finalizar o processo.</li>
        </ol>
        <p><strong>Senha temporária: {temp_password}</strong></p>
        <a href="{settings.FRONT_URL}">Ir para o Site</a>
        '''
