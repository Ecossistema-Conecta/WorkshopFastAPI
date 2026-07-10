from dataclasses import dataclass

import pytest
from redis.asyncio import Redis

from src.common.infra.repositories import RedisRepository


@dataclass
class SutTypes:
    sut: RedisRepository


@pytest.fixture
def make_sut(redis_client: Redis) -> SutTypes:
    sut = RedisRepository(redis_client)

    return SutTypes(sut=sut)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_should_return_the_value_for_a_given_key_on_success(make_sut: SutTypes, redis_client: Redis):
    sut = make_sut.sut

    key = 'test_key'
    value = 'test_value'
    await redis_client.set(name=key, value=value)

    response = await sut.get(key=key)

    assert response == value


@pytest.mark.unit
@pytest.mark.asyncio
async def test_insert_expires_should_save_the_value_for_a_given_key_on_success(make_sut: SutTypes, redis_client: Redis):
    sut = make_sut.sut

    key = 'inserted_test_key'
    value = 'Inserted_test_value'

    await sut.insert_expires(key=key, value=value, expires_in=60)

    expected_value = await redis_client.get(name=key)

    assert expected_value == value
