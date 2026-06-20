"""应用配置"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Agnes AI
    AGNES_API_KEY: str = "sk-axqioDe5kSeOY34IM9fQ1s8XZEGkOQzHpKwcc9ebwVYEjbNW"
    AGNES_API_BASE: str = "https://apihub.agnes-ai.com/v1"
    AGNES_DEFAULT_TEXT_MODEL: str = "agnes-2.0-flash"

    # 知识库
    KNOWLEDGE_CHUNK_SIZE: int = 500
    KNOWLEDGE_CHUNK_OVERLAP: int = 50

    # MySQL
    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "ai_customer_service"
    MYSQL_USER: str = "cs_user"
    MYSQL_PASSWORD: str = "cs_password"

    # Qdrant
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # App
    APP_NAME: str = "AI Customer Service"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
