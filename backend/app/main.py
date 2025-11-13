from __future__ import annotations

import os
import uuid
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.app.extractor import extract_readable_text
from backend.app.tts import text_to_wav

app = FastAPI(title="Narrador Web", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SpeakIn(BaseModel):
    html: str = Field(...)
    url: Optional[str] = Field(None)
    voice: Optional[str] = Field(None)
    rate: Optional[int] = Field(None)

class SpeakOut(BaseModel):
    run_id: str

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "out")
os.makedirs(OUT_DIR, exist_ok=True)

def _wav_path(run_id: str) -> str:
    return os.path.join(OUT_DIR, f"{run_id}.wav")

@app.get("/noop")
def noop():
    return {"ok": True}

@app.post("/speak", response_model=SpeakOut)
def speak(payload: SpeakIn):
    content_txt = extract_readable_text(payload.html, payload.url)
    if not content_txt or not content_txt.strip():
        raise HTTPException(status_code=422, detail="No se encontró texto legible en el HTML.")
    run_id = uuid.uuid4().hex
    wav_path = _wav_path(run_id)
    try:
        text_to_wav(
            text=content_txt,
            out_path=wav_path,
            voice_hint=payload.voice,
            rate=payload.rate,
        )
    except Exception as exc:
        logging.exception("TTS error")
        raise HTTPException(status_code=500, detail=f"Backend error (TTS): {exc}")
    return SpeakOut(run_id=run_id)

@app.get("/stream/{run_id}")
def stream(run_id: str):
    wav_path = _wav_path(run_id)
    if not os.path.exists(wav_path):
        raise HTTPException(status_code=404, detail="Audio no encontrado.")
    return FileResponse(path=wav_path, media_type="audio/wav", filename=f"{run_id}.wav")

# ========== SOLUCIÓN 2: Fix error 500 en cleanup ==========
@app.post("/cleanup/{run_id}")
def cleanup(run_id: str):
    """
    Intenta eliminar el archivo WAV después de reproducción.
    No falla con 500 si el archivo está en uso (común en Windows).
    """
    wav_path = _wav_path(run_id)
    
    if not os.path.exists(wav_path):
        return {"deleted": False, "reason": "not_found"}
    
    try:
        os.remove(wav_path)
        return {"deleted": True}
    
    except PermissionError:
        # Archivo en uso por el audio player del navegador
        # No es un error crítico, solo log
        logging.info(f"Cleanup: archivo {run_id}.wav en uso, no se pudo eliminar aún")
        return {"deleted": False, "reason": "file_in_use"}
    
    except Exception as exc:
        # Otro tipo de error (disco lleno, permisos, etc.)
        # Log pero no levanta 500
        logging.warning(f"Cleanup failed for {run_id}: {exc}")
        return {"deleted": False, "reason": str(exc)[:100]}  # Limitar mensaje

@app.get("/voices")
def voices():
    try:
        import pyttsx3
        eng = pyttsx3.init()
        out = []
        for v in eng.getProperty("voices"):
            out.append({
                "id": getattr(v, "id", ""),
                "name": getattr(v, "name", ""),
                "lang": getattr(v, "languages", [])
            })
        try:
            eng.stop()
        except Exception:
            pass
        return {"voices": out}
    except Exception as exc:
        return {"voices": [], "error": str(exc)}