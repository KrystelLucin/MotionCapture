# config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/app.db"
    AZURE_STORAGE_CONNECTION_STRING: str
    AZURE_SPEECH_KEY: str
    AZURE_SPEECH_REGION: str

    class Config:
        env_file = ".env"

settings = Settings()