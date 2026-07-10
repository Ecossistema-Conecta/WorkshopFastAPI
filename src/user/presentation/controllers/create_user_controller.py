from datetime import datetime, timedelta, time
from http import HTTPStatus
from random import randint
from typing import Annotated, Any
from unittest.mock import MagicMock
from uuid import uuid4

import bcrypt
import math
from fastapi import Depends
from mailersend import EmailBuilder, MailerSendClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from redis.asyncio import Redis

from src.common.domain.models import EmailCacheKeys, MailerAdapterResponse, EmailLogModel
from src.common.infra.entities import EmailLog
from src.common.presentation.helpers import created
from src.common.presentation.helpers.http_helper import too_many_requests
from src.common.presentation.http_types import HttpRequest, HttpResponse
from src.common.presentation.interfaces import IController
from src.exceptions.types import ConflictError
from src.main.config import get_session, get_redis_connection, settings
from src.user.domain.models import CreateUserModel, UserModel, EmailLogResponseModel
from src.user.infra.entities import User


class CreateUserController(IController):
    def __init__(
            self,
            session: Annotated[AsyncSession, Depends(get_session)],
            redis: Annotated[Redis, Depends(get_redis_connection)]
    ) -> None:
        self.__session = session
        self.__redis = redis

    async def handle(self, http_request: HttpRequest) -> HttpResponse:
        body: Any = http_request.body
        new_user = CreateUserModel(**body)

        db_user = await self.__session.scalar(select(User).where(User.email == new_user.email))
        user_found = None

        if db_user:
            user_found = UserModel.model_validate(db_user)

        if user_found:
            raise ConflictError('User already registered')

        temp_password = new_user.password

        binary_text = temp_password.encode('ascii')
        __salt = bcrypt.gensalt()
        hashed_text = bcrypt.hashpw(binary_text, __salt)

        new_user.password = hashed_text.decode('utf-8')

        user = User(name=new_user.name, email=new_user.email, password=new_user.password)

        self.__session.add(user)
        await self.__session.commit()
        await self.__session.refresh(user)

        created_user = UserModel.model_validate(user)

        key = EmailCacheKeys.EMAIL_RATE_LIMIT_QUOTA.value
        rate_limit_count = await self.__redis.get(key)

        now = datetime.now()
        reset_time = now + timedelta(days=1)
        reset_time = datetime.combine(reset_time.date(), time(0, 0, 0))
        diff = reset_time - now
        in_seconds = math.ceil(diff.total_seconds())

        if rate_limit_count == 0:
            retry_after = in_seconds + randint(1, 700)

            await self.__redis.set(key, 0, ex=in_seconds)

            email_log_response = EmailLogResponseModel(
                success=False,
                status_code=HTTPStatus.TOO_MANY_REQUESTS,
                error_message='Rate limit exceeded',
                retry_after=retry_after,
            )

            return too_many_requests(body=email_log_response.model_dump())

        body = f'''<h3>Prezado(a) usuário(a),</h3>
        Siga os passos abaixo para fazer seu primeiro acesso ao sistema:</p>
        <ol>
          <li>Faça login utilizando a senha temporária fornecida abaixo.</li>
          <li>Você será automaticamente redirecionado para uma página segura, onde poderá criar uma nova senha pessoal.</li>
          <li>Insira e confirme sua nova senha e, em seguida, clique em "Salvar" para finalizar o processo.</li>
        </ol>
        <p><strong>Senha temporária: {temp_password}</strong></p>
        <a href="{settings.FRONT_URL}">Ir para o Site</a>
        '''
        subject = str('Bem vindo(a) ao Projeto')

        email_id = None
        rate_limit_remaining = 0
        error_message = None

        email = (
            EmailBuilder()
            .from_email(email=settings.DEFAULT_EMAIL, name=settings.PROJECT_NAME)
            .to(email=created_user.email, name=created_user.name)
            .subject(subject=subject)
            .html(html_content=body)
            .build()
        )

        mailer_send_client = MailerSendClient()
        # response = mailer_send_client.emails.send(email=email)
        api_response = MagicMock()
        api_response.success = True
        api_response.status_code = 200
        api_response.request_id = str(uuid4())
        api_response.rate_limit_remaining = randint(1, 100)
        api_response.retry_after = None
        mailer_send_response = api_response

        status_code = mailer_send_response.status_code

        if mailer_send_response.success:
            email_id = mailer_send_response.request_id
            rate_limit_remaining = mailer_send_response.rate_limit_remaining if mailer_send_response.rate_limit_remaining else 0
        else:
            data = mailer_send_response.data
            error_message = data.get('message', 'Unknown error')

        mailer_response = MailerAdapterResponse(
            email_id=email_id,
            success=mailer_send_response.success,
            status_code=HTTPStatus(status_code),
            rate_limit_remaining=rate_limit_remaining,
            retry_after=mailer_send_response.retry_after,
            error_message=error_message,
        )

        status_code = mailer_response.status_code
        email_id = mailer_response.email_id
        remaining_quota = mailer_response.rate_limit_remaining

        if mailer_response.status_code == HTTPStatus.TOO_MANY_REQUESTS and mailer_response.retry_after:
            retry_after = mailer_response.retry_after + randint(1, 700)
            await self.__redis.set(key, remaining_quota, ex=in_seconds)

            new_email_log = EmailLog(
                id_control=email_id, receiver_id=created_user.id, sender_id=None, subject=subject, body=body,
                error='Rate limit exceeded'
            )

            self.__session.add(new_email_log)
            await self.__session.commit()
            await self.__session.refresh(new_email_log)

            created_email_log = EmailLogModel.model_validate(new_email_log)

            email_log_response = EmailLogResponseModel(
                success=False,
                log_id=created_email_log.id,
                status_code=status_code,
                error_message='Rate limit exceeded',
                retry_after=retry_after,
            )

            return too_many_requests(body=email_log_response.model_dump())

        if not mailer_send_response.success:
            new_email_log = EmailLog(
                id_control=email_id, receiver_id=created_user.id, sender_id=None, subject=subject, body=body,
                error=mailer_send_response.error_message
            )

            self.__session.add(new_email_log)
            await self.__session.commit()
            await self.__session.refresh(new_email_log)

            created_email_log = EmailLogModel.model_validate(new_email_log)

            email_log_response = EmailLogResponseModel(
                success=False, log_id=created_email_log.id, status_code=status_code, error_message=mailer_send_response.error_message
            )

            raise Exception(email_log_response.model_dump())

        await self.__redis.set(key, remaining_quota, ex=in_seconds)

        new_email_log = EmailLog(
            id_control=email_id, receiver_id=created_user.id, sender_id=None, subject=subject, body=body, error=None)

        self.__session.add(new_email_log)
        await self.__session.commit()
        await self.__session.refresh(new_email_log)

        return created()
