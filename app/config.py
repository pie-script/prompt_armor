from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "PromptArmor Gateway"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    LLM_GUARD_MODEL: str = "openai/gpt-oss-safeguard-20b"
    DOWNSTREAM_LLM_MODEL: str = "openai/gpt-oss-120b"  
    MAX_PROMPT_LENGTH: int = 4000


settings = Settings()
