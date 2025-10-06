from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = Field(default="btg-backend", alias="APP_NAME")
    app_env: str = Field(default="local", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    secret_key: str = Field(..., alias="SECRET_KEY")
    jwt_expire_minutes: int = Field(default=60, alias="JWT_EXPIRE_MINUTES")

    # API
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    allowed_hosts: str = Field(default="localhost,127.0.0.1", alias="ALLOWED_HOSTS")
    cors_origins: str = Field(default="http://localhost:3000,http://127.0.0.1:3000", alias="CORS_ORIGINS")
    disable_docs_in_prod: bool = Field(default=False, alias="DISABLE_DOCS_IN_PROD")

    # Mongo
    mongo_uri: str = Field(default="mongodb://localhost:27017", alias="MONGO_URI")
    mongo_db: str = Field(default="btg", alias="MONGO_DB")

    # Rate limit & logging
    rate_limit_default: str = Field(default="100/minute", alias="RATE_LIMIT_DEFAULT")
    rate_limit_storage_url: str = Field(default="redis://localhost:6379/0", alias="RATE_LIMIT_STORAGE_URL")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "populate_by_name": True,
        "extra": "ignore",
    }

settings = Settings()
