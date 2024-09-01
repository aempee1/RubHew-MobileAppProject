# rubhew/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SQLDB_URL: str
    SECRET_KEY: str = "secret"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5 * 60  # 5 minutes
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 7 * 24 * 60  # 7 days

    model_config = SettingsConfigDict(
        env_file=".env", validate_assignment=True, extra="allow"
    )

def get_settings(testing=False):
    settings = Settings()
    if testing:
        settings.SQLDB_URL = "sqlite+aiosqlite:///./test.db"
    return settings
