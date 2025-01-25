from pydantic import AnyUrl, BeforeValidator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated, Any


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../../../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    API_VERSION_STRING: str = "/api/v1"

    PROJECT_NAME: str
    PROJECT_DESCRIPTION: str
    PROJECT_VERSION: str

    FRONTEND_HOST: str = "http://localhost:5173"
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    SUPABASE_URL_IPV4: str
    SUPABASE_URL_IPV6: str
    SUPABASE_KEY: str

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [self.FRONTEND_HOST]


settings = Settings()
