import bcrypt
import pytest
from pytest_mock.plugin import MockerFixture

from src.common.infra.adapters import HasherAdapter


@pytest.fixture
def mock_bcrypt(mocker: MockerFixture) -> None:
    mock_hashpw = mocker.patch.object(bcrypt, 'hashpw', autospec=True)

    mock_hashpw.return_value = b'hashed_password'

    return mock_hashpw


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hash_should_return_a_hashed_password(mock_bcrypt: MockerFixture) -> None:
    sut = HasherAdapter()

    result = await sut.hash('password')

    assert isinstance(result, str)
    assert result == 'hashed_password'


@pytest.mark.unit
@pytest.mark.asyncio
async def test_should_call_hash_with_correct_values(mock_bcrypt: MockerFixture, mocker: MockerFixture) -> None:
    sut = HasherAdapter()

    hash_spy = mocker.spy(sut, 'hash')

    await sut.hash('password')

    hash_spy.assert_called_once_with('password')


@pytest.mark.unit
@pytest.mark.asyncio
async def test_should_raise_if_hash_raise_exception(mocker: MockerFixture) -> None:
    sut = HasherAdapter()

    mocker.patch(
        'src.common.infra.adapters.HasherAdapter.hash',
        side_effect=Exception('Test exception'),
    )

    with pytest.raises(Exception):  # noqa: PT011
        await sut.hash('password')
