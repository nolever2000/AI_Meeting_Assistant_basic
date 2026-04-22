from datetime import datetime
from pydantic import BaseModel


class RealtimeMessage(BaseModel):
    source: str
    original: str
    translated: str
    audio_base64: str | None = None
    timestamp: datetime


class HistoryRecord(BaseModel):
    id: int
    timestamp: datetime
    source: str
    original_text: str
    translated_text: str

    class Config:
        from_attributes = True
