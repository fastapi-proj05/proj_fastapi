from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USER: str = "root"
    DB_PASSWORD: str = "password1234"
    DB_HOST: str = "localhost"
    DB_PORT: str = "3306"
    DB_NAME: str = "ai_health"

    # Redis 설정 추가
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()