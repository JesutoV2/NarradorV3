from __future__ import annotations
from typing import Optional
import os
import time

def _choose_voice(engine, hint: Optional[str]) -> None:
    wanted = (hint or "").lower()
    voices = engine.getProperty("voices") or []
    chosen = None
    for v in voices:
        name = str(getattr(v, "name", "")).lower()
        if wanted and wanted in name:
            chosen = v.id
            break
        if "sabina" in name or "es-mx" in name:
            chosen = v.id
            break
    if not chosen:
        for v in voices:
            name = str(getattr(v, "name", "")).lower()
            if "es-" in name or "spanish" in name or "espa" in name:
                chosen = v.id
                break
    if chosen:
        engine.setProperty("voice", chosen)

def text_to_wav(text: str, out_path: str, voice_hint: Optional[str] = None, rate: Optional[int] = None) -> None:
    if not text or not text.strip():
        raise ValueError("Texto vacío para TTS.")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    try:
        import pyttsx3
    except Exception as exc:
        raise RuntimeError(f"pyttsx3 no disponible: {exc}")
    eng = pyttsx3.init()
    try:
        if rate:
            eng.setProperty("rate", int(rate))
        else:
            eng.setProperty("rate", 160)
        _choose_voice(eng, voice_hint)
        eng.save_to_file(text, out_path)
        eng.runAndWait()
    except Exception as run_exc:
        # Limpiar archivo corrupto si pyttsx3 falla a la mitad
        if os.path.exists(out_path):
            try:
                os.remove(out_path)
            except Exception:
                pass
        raise RuntimeError(f"Error en motor TTS: {run_exc}")
    finally:
        try:
            eng.stop()
        except Exception:
            pass
    for _ in range(50):
        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            return
        time.sleep(0.1)
        
    # Limpiar archivo si falló por timeout (ej. tamaño 0)
    if os.path.exists(out_path):
        try:
            os.remove(out_path)
        except Exception:
            pass
    raise RuntimeError("No se generó el WAV a tiempo.")
