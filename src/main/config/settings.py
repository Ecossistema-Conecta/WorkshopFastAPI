from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )  # pyright: ignore[reportUnannotatedClassAttribute]

    ''' Project name '''
    PROJECT_NAME: str = 'Projeto'

    ''' Database connection params '''

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    @computed_field  # type: ignore
    @property
    def DATABASE_URL(self) -> str:
        return f'postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    ''' Redis connection params '''

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    @computed_field  # type: ignore
    @property
    def REDIS_URL(self) -> str:
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}'

    ''' Email related environment variables '''

    DEFAULT_EMAIL: str
    MAILERSEND_API_KEY: str

    ''' Frontend url sent to change password '''

    FRONT_URL: str


settings = Settings()  # pyright: ignore[reportCallIssue]
