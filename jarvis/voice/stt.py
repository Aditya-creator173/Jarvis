from __future__ import annotations
import tempfile
import numpy as np
import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel
from jarvis.config import CFG
from jarvis.logger import get_logger

log = get_logger(__name__)
_model = None

def _get_model():
    global _model
    if _model is None:
        log.info("Loading Whisper model...")
        _model = WhisperModel(
            CFG["voice"]["stt_model"],
            device=CFG["voice"]["stt_device"],
            compute_type=CFG["voice"]["stt_compute_type"]
        )
        log.info("Whisper ready.")
    return _model

def transcribe_file(path: str) -> str:
    model = _get_model()
    segments, _ = model.transcribe(path, beam_size=3, language="en")
    return " ".join(s.text.strip() for s in segments).strip()

def record_and_transcribe(silence_sec: float = None) -> str:
    silence = silence_sec or CFG["voice"]["silence_threshold_seconds"]
    sr = CFG["voice"]["audio_sample_rate"]
    log.info("Listening...")
    chunk_size = int(sr * 0.1)
    silence_chunks = int(silence / 0.1)
    chunks, silent_count, started = [], 0, False
    threshold = 0.01

    with sd.InputStream(samplerate=sr, channels=1, dtype="float32") as stream:
        while True:
            data, _ = stream.read(chunk_size)
            rms = float(np.sqrt(np.mean(data**2)))
            if rms > threshold:
                started = True
                silent_count = 0
            elif started:
                silent_count += 1
            if started:
                chunks.append(data.copy())
            if started and silent_count >= silence_chunks:
                break

    if not chunks:
        return ""
    audio = np.concatenate(chunks, axis=0)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, audio, sr)
        return transcribe_file(f.name)
