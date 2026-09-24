from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "PromptArmor Gateway"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    MAX_PROMPT_LENGTH: int = 4000


settings = Settings()
