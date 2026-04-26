import base64
import logging
from io import BytesIO

from backend.config import Settings

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = None
        if settings.openai_api_key and OpenAI:
            self.client = OpenAI(api_key=settings.openai_api_key)
        elif settings.openai_api_key:
            logger.warning('openai package is not installed. Falling back to no-op services.')

    async def transcribe_pcm16(self, pcm_audio: bytes, sample_rate: int) -> str:
        if not self.client:
            return ''

        wav_bytes = self._pcm_to_wav_bytes(pcm_audio, sample_rate)
        result = self.client.audio.transcriptions.create(
            model='gpt-4o-mini-transcribe',
            file=('chunk.wav', wav_bytes, 'audio/wav'),
            response_format='text',
        )
        return result.strip() if isinstance(result, str) else str(result)

    async def translate_text(self, text: str, target_language: str) -> str:
        if not text:
            return ''
        if not self.client:
            return f'[{target_language}] {text}'

        completion = self.client.responses.create(
            model='gpt-4.1-mini',
            input=[
                {
                    'role': 'system',
                    'content': (
                        'You are a real-time interpreter. Keep meaning, preserve tone, and output only the translation.'
                    ),
                },
                {
                    'role': 'user',
                    'content': f'Target language: {target_language}\nText: {text}',
                },
            ],
            temperature=0.2,
        )
        return completion.output_text.strip()

    async def text_to_speech_base64(self, text: str, voice: str = 'alloy') -> str | None:
        if not text:
            return None
        if not self.client:
            return None

        response = self.client.audio.speech.create(
            model='gpt-4o-mini-tts',
            voice=voice,
            input=text,
            response_format='mp3',
        )
        audio_bytes = response.read()
        return base64.b64encode(audio_bytes).decode('utf-8')

    @staticmethod
    def _pcm_to_wav_bytes(pcm_audio: bytes, sample_rate: int) -> bytes:
        import wave

        with BytesIO() as bio:
            with wave.open(bio, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(pcm_audio)
            return bio.getvalue()
