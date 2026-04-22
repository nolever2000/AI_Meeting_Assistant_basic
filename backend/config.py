from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'Realtime Speech Translator'
    openai_api_key: str | None = Field(default=None, alias='OPENAI_API_KEY')
    database_url: str = 'sqlite:///./translator.db'

    mic_device: str | int | None = None
    speaker_loopback_device: str | int | None = None
    sample_rate: int = 16000
    chunk_ms: int = 400
    vad_mode: int = 2
    min_speech_ms: int = 600
    silence_ms_to_finalize: int = 700

    mic_target_language: str = 'en'
    speaker_target_language: str = 'vi'


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
