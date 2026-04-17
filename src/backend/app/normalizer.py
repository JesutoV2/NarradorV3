from __future__ import annotations

import re
from typing import List

_WS_RE = re.compile(r'\s+')
_MULTI_NL_RE = re.compile(r'\n{3,}')

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r", "\n")
    text = _MULTI_NL_RE.sub("\n\n", text)
    text = _WS_RE.sub(" ", text)
    return text.strip()

def long_enough(text: str, min_chars: int = 60) -> bool:
    return bool(text) and len(text) >= min_chars

def split_paragraphs(text: str, max_length: int = 800) -> List[str]:    
    if not text:
        return []
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    out: List[str] = []
    for b in blocks:
        if long_enough(b, min_chars):
            out.append(b)
    if not out and long_enough(text, min_chars):
        out = [text.strip()]
    return out

def pretty_join(items: List[str]) -> str:
    return "\n\n".join(items)
