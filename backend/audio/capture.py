import asyncio
import logging
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)

try:
    import sounddevice as sd
except ImportError:  # pragma: no cover
    sd = None


@dataclass
class AudioChunk:
    source: str
    pcm16: bytes


class AudioCaptureWorker:
    def __init__(
        self,
        source: str,
        queue: asyncio.Queue[AudioChunk],
        sample_rate: int,
        chunk_ms: int,
        device: str | int | None = None,
        loopback: bool = False,
    ) -> None:
        self.source = source
        self.queue = queue
        self.sample_rate = sample_rate
        self.frames_per_chunk = int(sample_rate * (chunk_ms / 1000.0))
        self.device = device
        self.loopback = loopback
        self._stream = None

    def start(self, event_loop: asyncio.AbstractEventLoop) -> None:
        if not sd:
            logger.warning('sounddevice not installed, %s capture disabled', self.source)
            return

        extra = None
        if self.loopback:
            extra = sd.WasapiSettings(loopback=True)

        def callback(indata, frames, time_info, status):  # noqa: ANN001
            if status:
                logger.debug('%s status: %s', self.source, status)
            mono = indata[:, 0] if indata.ndim > 1 else indata
            pcm16 = (np.clip(mono, -1, 1) * 32767).astype(np.int16).tobytes()
            event_loop.call_soon_threadsafe(
                self.queue.put_nowait,
                AudioChunk(source=self.source, pcm16=pcm16),
            )

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            blocksize=self.frames_per_chunk,
            channels=1,
            dtype='float32',
            callback=callback,
            device=self.device,
            extra_settings=extra,
        )
        self._stream.start()
        logger.info('Started %s capture (device=%s, loopback=%s)', self.source, self.device, self.loopback)

    def stop(self) -> None:
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
