import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone

from backend.ai.openai_services import OpenAIService
from backend.audio.capture import AudioChunk
from backend.audio.vad import SpeechGate
from backend.config import Settings
from backend.db.database import add_history
from backend.websocket import WebSocketManager


@dataclass
class SourceBuffer:
    active: bool = False
    speech_ms: int = 0
    silence_ms: int = 0
    chunks: list[bytes] = field(default_factory=list)


class RealtimePipeline:
    def __init__(self, settings: Settings, ws_manager: WebSocketManager, ai: OpenAIService):
        self.settings = settings
        self.ws_manager = ws_manager
        self.ai = ai
        self.queue: asyncio.Queue[AudioChunk] = asyncio.Queue(maxsize=200)
        self.vad = SpeechGate(mode=settings.vad_mode, sample_rate=settings.sample_rate)
        self.buffers = {'mic': SourceBuffer(), 'speaker': SourceBuffer()}
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        self._task = asyncio.create_task(self._run(), name='realtime-pipeline')

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

    async def _run(self) -> None:
        chunk_ms = self.settings.chunk_ms
        while True:
            chunk = await self.queue.get()
            state = self.buffers[chunk.source]
            is_speech = self.vad.has_speech(chunk.pcm16)

            if is_speech:
                state.active = True
                state.speech_ms += chunk_ms
                state.silence_ms = 0
                state.chunks.append(chunk.pcm16)
                continue

            if state.active:
                state.silence_ms += chunk_ms
                if state.silence_ms <= self.settings.silence_ms_to_finalize:
                    state.chunks.append(chunk.pcm16)

                if state.speech_ms >= self.settings.min_speech_ms and state.silence_ms >= self.settings.silence_ms_to_finalize:
                    pcm = b''.join(state.chunks)
                    await self._process_segment(chunk.source, pcm)
                    self.buffers[chunk.source] = SourceBuffer()
                elif state.silence_ms > self.settings.silence_ms_to_finalize + 1000:
                    self.buffers[chunk.source] = SourceBuffer()

    async def _process_segment(self, source: str, pcm16: bytes) -> None:
        original = (await self.ai.transcribe_pcm16(pcm16, self.settings.sample_rate)).strip()
        if not original:
            return

        target = self.settings.mic_target_language if source == 'mic' else self.settings.speaker_target_language
        translated = await self.ai.translate_text(original, target_language=target)
        audio_base64 = None
        if source == 'mic':
            audio_base64 = await self.ai.text_to_speech_base64(translated)

        ts = datetime.now(timezone.utc)
        add_history(source=source, original_text=original, translated_text=translated, timestamp=ts)

        payload = {
            'source': source,
            'original': original,
            'translated': translated,
            'audio_base64': audio_base64,
            'timestamp': ts.isoformat(),
        }
        await self.ws_manager.broadcast(payload)


import contextlib
