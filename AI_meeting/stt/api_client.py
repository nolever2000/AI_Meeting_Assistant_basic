import io
import soundfile as sf
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def transcribe(audio_np):
    buffer = io.BytesIO()
    sf.write(buffer, audio_np, 16000, format="WAV")
    buffer.seek(0)

    res = client.audio.transcriptions.create(
        file=buffer,
        model="gpt-4o-mini-transcribe"
    )

    return res.text