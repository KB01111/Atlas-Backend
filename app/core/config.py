from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    OPENAI_API_KEY: str
    LITELLM_API_KEY: str
    LOG_LEVEL: str = "INFO"
    BACKEND_CORS_ORIGINS: str = "*"

    model_config = SettingsConfigDict(env_file=".env")

# Lazy-load settings: do NOT instantiate at module level
_settings_instance = None

def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
