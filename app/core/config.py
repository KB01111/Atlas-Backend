from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    LITELLM_API_KEY: str = Field(..., env="LITELLM_API_KEY")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    BACKEND_CORS_ORIGINS: str = Field("*", env="BACKEND_CORS_ORIGINS")

    class Config:
        env_file = ".env"

settings = Settings()