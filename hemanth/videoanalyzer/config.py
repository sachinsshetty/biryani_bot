from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    AI_API_URL: str
    AI_MODEL_NAME: str
    VIDEO_INPUT_PATH: str
    DWANI_API_URL: str
    DWANI_API_KEY: str
    AI_CLOUD_API_URL: str
    AI_CLOUD_API_KEY: str
    AI_CLOUD_API_VISION_MODEL_NAME: str
    AI_CLOUD_API_TEXT_MODEL_NAME: str
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()