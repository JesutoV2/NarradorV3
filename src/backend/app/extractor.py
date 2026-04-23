from __future__ import annotations

from typing import List, Optional
import re

from bs4 import BeautifulSoup, Tag

from app.normalizer import normalize_text, split_paragraphs, long_enough, pretty_join
from app.filters import clean_html_and_pick

def _parse(html: str) -> BeautifulSoup:
    try:
        return BeautifulSoup(html, "lxml")
    except Exception:
        return BeautifulSoup(html, "html.parser")

def _is_hidden(tag: Tag) -> bool:
    if not isinstance(tag, Tag):
        return False
    try:
        if tag.has_attr("hidden"):
            return True
        if tag.has_attr("aria-hidden") and str(tag["aria-hidden"]).lower() == "true":
            return True
    except Exception:
        pass
    style = (tag.get("style") or "").lower()
    if "display:none" in style or "visibility:hidden" in style:
        return True
    cls = " ".join(tag.get("class") or []).lower()
    if "visually-hidden" in cls or "sr-only" in cls:
        return True
    return False

def _harvest_paragraphs(root: Tag, min_chars: int = 60) -> List[str]:
    parts: List[str] = []
    
    # ========== SOLUCIÓN 1 MEJORADA: Extraer en ORDEN del DOM ==========
    
    # UNA SOLA PASADA: Recorrer todos los elementos en orden de aparición
    for elem in root.find_all(["h1", "h2", "h3", "p", "li", "blockquote"]):
        if _is_hidden(elem):
            continue
        
        txt = normalize_text(elem.get_text(" ", strip=True))
        if not txt:
            continue
        
        # Clasificar según tipo y longitud
        if elem.name in ["h1", "h2", "h3"]:
            # Headers
            if 5 <= len(txt) < 150:
                # Título corto/medio (5-149 chars)
                parts.append(txt)
                print(f"[DEBUG EXTRACTOR] Título <{elem.name}> ({len(txt)} chars): {txt[:60]}...")
            elif len(txt) >= 150:
                # Contenido largo en header (≥150 chars, caso DGCS)
                parts.append(txt)
                print(f"[DEBUG EXTRACTOR] Contenido en <{elem.name}> ({len(txt)} chars): {txt[:80]}...")
            # else: Header muy corto (<5 chars), ignorar
        
        elif elem.name in ["p", "li", "blockquote"]:
            # Contenido normal
            if long_enough(txt, min_chars):
                parts.append(txt)
    
    # 4. Fallback: si no hay nada, buscar en section/article
    if not parts:
        for sect in root.find_all(["article", "section"]):
            if _is_hidden(sect):
                continue
            txt = normalize_text(sect.get_text(" ", strip=True))
            if long_enough(txt, min_chars * 2):
                parts.extend(split_paragraphs(txt, min_chars=min_chars))
    
    # 5. Último recurso: extraer todo el texto y dividir
    if not parts:
        txt = normalize_text(root.get_text(" ", strip=True))
        parts = split_paragraphs(txt, min_chars=min_chars)
    
    # 6. Deduplicación (pero manteniendo orden)
    seen = set()
    out: List[str] = []
    for t in parts:
        # Normalizar para comparación (eliminar espacios extras)
        t_normalized = " ".join(t.split())
        if t_normalized and t_normalized not in seen:
            seen.add(t_normalized)
            out.append(t)
    
    return out

def extract_readable_text(html: str, url: Optional[str] = None) -> str:
    print(f"\n[DEBUG EXTRACTOR] ========== INICIANDO EXTRACCIÓN ==========")
    print(f"[DEBUG EXTRACTOR] URL: {url}")
    print(f"[DEBUG EXTRACTOR] HTML size: {len(html)} bytes")
    
    # Integración con filters.py
    cleaned_html = clean_html_and_pick(html)
    
    # Parsear el HTML ya limpio
    container = _parse(cleaned_html)
    
    # Prints de debug
    print(f"[DEBUG EXTRACTOR] Container después de filters: <{container.name}>")
    container_id = container.get('id') if hasattr(container, 'get') else None
    container_class = container.get('class') if hasattr(container, 'get') else None
    print(f"[DEBUG EXTRACTOR] Container ID: {container_id}")
    print(f"[DEBUG EXTRACTOR] Container CLASS: {container_class}")
    
    container_text = container.get_text(" ", strip=True) if container else ""
    print(f"[DEBUG EXTRACTOR] Chars en container: {len(container_text)}")
    
    # Extraer párrafos (ahora incluye títulos + contenido)
    paragraphs = _harvest_paragraphs(container, min_chars=60)
    
    print(f"[DEBUG EXTRACTOR] Párrafos encontrados: {len(paragraphs)}")
    if paragraphs:
        print(f"[DEBUG EXTRACTOR] Primer párrafo ({len(paragraphs[0])} chars): {paragraphs[0][:100]}...")
        print(f"[DEBUG EXTRACTOR] Total chars extraídos: {sum(len(p) for p in paragraphs)}")
    else:
        print(f"[DEBUG EXTRACTOR] ⚠️ NO SE ENCONTRARON PÁRRAFOS")
    
    text = pretty_join(paragraphs)
    print(f"[DEBUG EXTRACTOR] Texto final: {len(text)} chars")
    print(f"[DEBUG EXTRACTOR] ========== FIN EXTRACCIÓN ==========\n")
    return text
