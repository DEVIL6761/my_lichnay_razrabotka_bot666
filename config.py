from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    bot_token: str
    db_url: str  # ← без значения по умолчанию → будет браться из .env

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()