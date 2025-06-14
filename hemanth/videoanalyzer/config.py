from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    AI_API_URL: str
    AI_MODEL_NAME: str
    VIDEO_INPUT_PATH: str
    DWANI_API_URL: str
    DWANI_API_KEY: str
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()