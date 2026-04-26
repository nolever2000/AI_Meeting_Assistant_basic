import asyncio
import logging
from datetime import datetime

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.ai.openai_services import OpenAIService
from backend.audio.capture import AudioCaptureWorker
from backend.config import get_settings
from backend.db.database import init_db, list_history
from backend.models.schemas import HistoryRecord
from backend.pipeline.processor import RealtimePipeline
from backend.websocket import WebSocketManager

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

ws_manager = WebSocketManager()
ai_service = OpenAIService(settings)
pipeline = RealtimePipeline(settings=settings, ws_manager=ws_manager, ai=ai_service)

mic_capture: AudioCaptureWorker | None = None
speaker_capture: AudioCaptureWorker | None = None


@app.on_event('startup')
async def startup_event() -> None:
    global mic_capture, speaker_capture

    init_db()
    pipeline.start()
    loop = asyncio.get_running_loop()

    mic_capture = AudioCaptureWorker(
        source='mic',
        queue=pipeline.queue,
        sample_rate=settings.sample_rate,
        chunk_ms=settings.chunk_ms,
        device=settings.mic_device,
    )
    speaker_capture = AudioCaptureWorker(
        source='speaker',
        queue=pipeline.queue,
        sample_rate=settings.sample_rate,
        chunk_ms=settings.chunk_ms,
        device=settings.speaker_loopback_device,
        loopback=True,
    )
    mic_capture.start(loop)
    speaker_capture.start(loop)


@app.on_event('shutdown')
async def shutdown_event() -> None:
    if mic_capture:
        mic_capture.stop()
    if speaker_capture:
        speaker_capture.stop()


@app.get('/health')
async def health() -> dict:
    return {'status': 'ok'}


@app.get('/history', response_model=list[HistoryRecord])
async def get_history(
    source: str | None = Query(default=None),
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
) -> list[HistoryRecord]:
    rows = list_history(source=source, start=start, end=end)
    return [
        HistoryRecord(
            id=row.id,
            timestamp=row.timestamp,
            source=row.source,
            original_text=row.original_text,
            translated_text=row.translated_text,
        )
        for row in rows
    ]


@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket) -> None:
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
