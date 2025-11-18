from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    bot_token: str = "8562525316:AAExzpu3vhre9HZWxJvTb6JyE8kQnGHphZs" # ← Обязательно должен быть
    db_url: str = "postgresql+asyncpg://postgres:1234567891@localhost:5432/job_bot_db"

    class Config:
        env_file = ".env"

settings = Settings()