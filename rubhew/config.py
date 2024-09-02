from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SQLDB_URL: str
    TEST_SQLDB_URL: str = "sqlite+aiosqlite:///./test.db"
    SECRET_KEY: str = "secret"
    TESTING: bool = False  # Flag for testing environment

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5 * 60  # 5 hours
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 7 * 24 * 60  # 7 days

    model_config = SettingsConfigDict(
        env_file=".env", validate_assignment=True, extra="allow"
    )

def get_settings(testing=False):
    settings = Settings()
    settings.TESTING = testing
    if testing:
        settings.SQLDB_URL = settings.TEST_SQLDB_URL
    return settings
