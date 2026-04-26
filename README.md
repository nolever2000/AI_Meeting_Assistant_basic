# Real-time Bidirectional Speech Translation (Windows + Web)

Production-oriented MVP for real-time conversation translation with a FastAPI backend and React frontend.

## Features

- Parallel audio pipelines:
  - `mic` (headset microphone) -> STT -> translate to configurable target (default `en`) -> TTS -> WebSocket.
  - `speaker` (WASAPI loopback of system/headset output) -> STT -> translate to Vietnamese (`vi`) -> WebSocket.
- Voice Activity Detection (WebRTC VAD) to process speech-only chunks.
- Real-time UI over WebSocket (`/ws`).
- Conversation history persisted in SQLite and queryable via `GET /history`.
- Modular backend layout for adding diarization, Teams/Zoom integration, etc.

## Project structure

```text
backend/
  main.py
  websocket.py
  config.py
  audio/
  ai/
  db/
  models/
  pipeline/
frontend/
  src/
    components/
```

## Backend setup (Windows PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env`:

```env
OPENAI_API_KEY=your_openai_key
MIC_DEVICE=Headset Microphone Name or device index
SPEAKER_LOOPBACK_DEVICE=Headset Speaker Name or device index
SAMPLE_RATE=16000
CHUNK_MS=400
MIC_TARGET_LANGUAGE=en
SPEAKER_TARGET_LANGUAGE=vi
```

Run backend:

```powershell
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend setup

```powershell
cd frontend
npm install
npm run dev
```

Optional frontend env (`frontend/.env`):

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

## Audio device configuration on Windows

1. List devices in Python shell:
   ```python
   import sounddevice as sd
   print(sd.query_devices())
   ```
2. Set `MIC_DEVICE` to your headset mic input device.
3. Set `SPEAKER_LOOPBACK_DEVICE` to your headset speaker/output endpoint that supports WASAPI loopback.
4. If loopback is unavailable on your endpoint, use VB-CABLE/virtual audio cable and bind loopback to that output.

## Real-time data contract (`/ws`)

```json
{
  "source": "mic",
  "original": "Xin chao",
  "translated": "Hello",
  "audio_base64": "...",
  "timestamp": "2026-04-22T10:00:00.000000+00:00"
}
```

## REST API

- `GET /history`
- `GET /history?source=mic`
- `GET /history?start=2026-04-22T00:00:00Z&end=2026-04-22T23:59:59Z`

## Performance + reliability notes

- Keep chunk sizes 300-500 ms (`CHUNK_MS=400` default).
- For sub-2s latency, use low buffering and avoid waiting for full sentences (segment finalization triggered by VAD silence timeout).
- Echo loop mitigation:
  - Prefer closed-back headset and separate input/output devices.
  - Keep speaker translation TTS disabled (current behavior) to avoid feedback loops.
  - Add AEC/noise suppression if using open speakers.

## MVP delivered

- Real-time mic + speaker capture pipeline
- VAD speech gate
- STT + translation + mic TTS
- Live WebSocket UI
- SQLite history

## Optional extension ideas

- Speaker diarization
- Dynamic language switching per source
- Subtitle overlay mode
- Export to CSV/JSON
- Zoom/Teams virtual audio adapters
