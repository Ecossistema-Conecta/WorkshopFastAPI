import pytest

from src.user.domain.models.user import CreateUserModel


@pytest.mark.unit
@pytest.mark.asyncio
async def test_user_model_generate_random_password_should_return_an_instance_with_random_password() -> None:
    new_user = {
        'name': 'test name',
        'email': 'test@test.com',
    }
    expected_password_length = 12

    user = CreateUserModel(**new_user)  # type: ignore

    assert user.password is not None
    assert isinstance(user.password, str)
    assert len(user.password) == expected_password_length
