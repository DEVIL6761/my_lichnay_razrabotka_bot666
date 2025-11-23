from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    bot_token: str
    db_url: str = os.getenv("DATABASE_URL")  # ← Railway использует это имя

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()