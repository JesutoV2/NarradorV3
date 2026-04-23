from __future__ import annotations

import os
import uuid
import logging
import glob
import sys
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from app.extractor import extract_readable_text
from app.tts import text_to_wav

# Integración con base de datos
try:
    from app import db
    DB_AVAILABLE = True
except Exception as e:
    DB_AVAILABLE = False
    print(f"Base de datos no disponible: {e}")

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

# Ajuste de ruta para compatibilidad con PyInstaller
if getattr(sys, 'frozen', False):
    # Si corre como ejecutable, la carpeta out va junto al .exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..")

OUT_DIR = os.path.join(BASE_DIR, "out")
os.makedirs(OUT_DIR, exist_ok=True)

def _wav_path(run_id: str) -> str:
    return os.path.join(OUT_DIR, f"{run_id}.wav")

@app.get("/noop")
def noop():
    return {"ok": True}

def calculate_ttcu(time_extract_ms: int, time_tts_ms: int) -> float:
    """Calcula Tiempo Hasta Contenido Útil en segundos."""
    return (time_extract_ms + time_tts_ms) / 1000.0

def calculate_ptnn(chars_original: int, chars_extracted: int) -> float:
    """Calcula Proporción de Texto No-Informativo."""
    if chars_original == 0:
        return 0.0
    text_removed = chars_original - chars_extracted
    ptnn = (text_removed / chars_original) * 100.0
    return max(0.0, min(100.0, ptnn))

@app.post("/speak", response_model=SpeakOut)
def speak(payload: SpeakIn):
    import time
    
    # PASO 0: Limpieza total de audios previos (evita acumulación de basura)
    for f in glob.glob(os.path.join(OUT_DIR, "*.wav")):
        try:
            os.remove(f)
            print(f"[CLEANUP] Archivo residual eliminado: {os.path.basename(f)}")
        except Exception as e:
            logging.warning(f"No se pudo limpiar {f}: {e}")

    run_id = uuid.uuid4().hex
    wav_path = _wav_path(run_id)
    start_time_total = time.time()
    
    # Variables para métricas
    chars_original = len(payload.html)
    chars_extracted = 0
    time_extract_ms = 0
    time_tts_ms = 0
    
    try:
        # PASO 1: Extracción
        start_extract = time.time()
        content_txt = extract_readable_text(payload.html, payload.url)
        time_extract_ms = int((time.time() - start_extract) * 1000)
        chars_extracted = len(content_txt) if content_txt else 0
        
        if not content_txt or not content_txt.strip():
            raise HTTPException(status_code=422, detail="No se encontró texto legible en el HTML.")
        
        # PASO 2: TTS
        start_tts = time.time()
        text_to_wav(
            text=content_txt,
            out_path=wav_path,
            voice_hint=payload.voice,
            rate=payload.rate,
        )
        time_tts_ms = int((time.time() - start_tts) * 1000)
        
        # PASO 3: Calcular métricas
        ttcu_seconds = calculate_ttcu(time_extract_ms, time_tts_ms)
        ptnn_percent = calculate_ptnn(chars_original, chars_extracted)
        
        # PASO 4: Registrar en BD (si está disponible)
        if DB_AVAILABLE and payload.url:
            try:
                page_id = db.upsert_page(url=payload.url)
                total_time_ms = int((time.time() - start_time_total) * 1000)
                words_count = len(content_txt.split())
                audio_duration_ms = int((words_count / 150.0) * 60 * 1000)
                
                db.insert_run(
                    run_id=run_id,
                    page_id=page_id,
                    url=payload.url,
                    ttcu_seconds=ttcu_seconds,
                    ptnn_percent=ptnn_percent,
                    total_time_ms=total_time_ms,
                    audio_duration_ms=audio_duration_ms,
                    chars_original=chars_original,
                    chars_extracted=chars_extracted,
                    ok=True,
                    err_msg=None
                )
                print(f"✅ Run {run_id[:8]}... registrado | TTCU: {ttcu_seconds:.2f}s | PTNN: {ptnn_percent:.1f}%")
            except Exception as db_exc:
                print(f"⚠️ Error registrando en BD: {db_exc}")
        
        return SpeakOut(run_id=run_id)
    
    except HTTPException:
        if os.path.exists(wav_path):
            try: os.remove(wav_path)
            except: pass
        raise
    except Exception as exc:
        if os.path.exists(wav_path):
            try: os.remove(wav_path)
            except: pass
        logging.exception("Error en backend")
        raise HTTPException(status_code=500, detail=f"Backend error: {exc}")



@app.get("/stream/{run_id}")
def stream(run_id: str):
    wav_path = _wav_path(run_id)
    if not os.path.exists(wav_path):
        raise HTTPException(status_code=404, detail="Audio no encontrado.")
    return FileResponse(path=wav_path, media_type="audio/wav", filename=f"{run_id}.wav")

# ========== SOLUCIÃ“N 2: Fix error 500 en cleanup ==========
@app.post("/cleanup/{run_id}")
def cleanup(run_id: str):
    """
    Intenta eliminar el archivo WAV despuÃ©s de reproducciÃ³n.
    No falla con 500 si el archivo estÃ¡ en uso (comÃºn en Windows).
    """
    wav_path = _wav_path(run_id)
    
    if not os.path.exists(wav_path):
        return {"deleted": False, "reason": "not_found"}
    
    try:
        os.remove(wav_path)
        return {"deleted": True}
    
    except PermissionError:
        # Archivo en uso por el audio player del navegador
        # No es un error crÃ­tico, solo log
        logging.info(f"Cleanup: archivo {run_id}.wav en uso, no se pudo eliminar aÃºn")
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
    
@app.get("/stats")
def stats():
    """Obtiene estadísticas de la base de datos."""
    if not DB_AVAILABLE:
        return {"db_available": False, "error": "Base de datos no disponible"}
    
    try:
        stats_data = db.get_stats()
        stats_data["db_available"] = True
        return stats_data
    except Exception as exc:
        return {"db_available": True, "error": str(exc)}
    
    