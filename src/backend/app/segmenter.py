# segmenter.py — segmentación y deduplicación
# - Corta por saltos de línea y puntuación fuerte
# - Deduplicación consecutiva
# - Deduplicación global ligera por hash de prefijo normalizado

import re
from typing import List

SENTENCE_SPLIT = re.compile(r"([.!?…]+)\s+")
SPACES = re.compile(r"\s+")

def _normalize_for_hash(s: str) -> str:
    s = s.lower()
    s = SPACES.sub(" ", s)
    return s.strip()

def _split_sentences(text: str) -> List[str]:
    # Primero por saltos de línea, luego por puntuación dentro de cada línea
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    out = []
    for ln in lines:
        buf = []
        start = 0
        for m in SENTENCE_SPLIT.finditer(ln + " "):
            end = m.end()
            seg = ln[start:end].strip()
            if seg:
                buf.append(seg)
            start = end
        if start < len(ln):
            tail = ln[start:].strip()
            if tail:
                buf.append(tail)
        if not buf and ln:
            buf = [ln]
        out.extend(buf)
    return [s for s in out if s]

def dedup_segments(segments: List[str]) -> List[str]:
    out = []
    seen = set()
    prev = ""
    for s in segments:
        norm = _normalize_for_hash(s)
        if not norm:
            continue
        # dedup consecutivo
        if norm == prev:
            continue
        prev = norm
        # dedup global ligera por prefijo
        key = norm[:120]
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out

def segment_text(text: str) -> List[str]:
    if not text or not isinstance(text, str):
        return []
    segs = _split_sentences(text)
    segs = [s for s in segs if len(_normalize_for_hash(s)) >= 3]
    segs = dedup_segments(segs)
    return segs
