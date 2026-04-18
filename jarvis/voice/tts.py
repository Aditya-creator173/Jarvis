from __future__ import annotations
import sounddevice as sd
import numpy as np
from jarvis.config import CFG
from jarvis.logger import get_logger

log = get_logger(__name__)
_pipeline = None

def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        try:
            from kokoro import KPipeline
            _pipeline = KPipeline(lang_code="a")
            log.info("Kokoro TTS ready.")
        except Exception as e:
            log.warning(f"Kokoro TTS failed to load: {e}. Voice output disabled.")
    return _pipeline

def speak(text: str):
    pipeline = _get_pipeline()
    if pipeline is None:
        print(f"[Jarvis]: {text}")
        return
    try:
        voice = CFG["voice"]["tts_voice"]
        speed = CFG["voice"]["tts_speed"]
        sr = 24000
        generator = pipeline(text, voice=voice, speed=speed)
        for _, _, audio in generator:
            if audio is not None and len(audio) > 0:
                sd.play(audio, samplerate=sr, blocking=True)
    except Exception as e:
        log.error(f"TTS error: {e}")
        print(f"[Jarvis]: {text}")
