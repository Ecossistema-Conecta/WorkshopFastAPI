import secrets
import string
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from src.common.domain.models import ProjectBaseModel


class UserBase(BaseModel):
    name: str = Field(max_length=100)
    email: EmailStr = Field(max_length=100)


class CreateUserModel(UserBase, validate_assignment=True):
    password: str

    @model_validator(mode='before')
    def generate_random_password(cls, data: dict[Any, Any], length: int = 12) -> dict[Any, Any]:
        if data.get('password', None) is None:
            characters = string.ascii_letters + string.digits + string.punctuation

            password = ''.join(secrets.choice(characters) for i in range(length))  # pyright: ignore[reportUnusedVariable]

            data['password'] = password

        return data


class UserModel(UserBase, ProjectBaseModel):
    is_superuser: bool = False

    model_config = ConfigDict(from_attributes=True)  # pyright: ignore[reportUnannotatedClassAttribute]
