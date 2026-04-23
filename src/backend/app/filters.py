# backend/app/filters.py
from __future__ import annotations
from bs4 import BeautifulSoup, Tag
import re

HIDDEN_CLASS_HINTS = {
    "visually-hidden", "sr-only", "is-hidden", "hidden", "u-hidden",
    "offscreen", "screen-reader-text"
}
# estilos inline que ocultan
STYLE_HIDE_PAT = re.compile(
    r"(display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0(\.0+)?|text-indent\s*:\s*-\d{3,}|clip-path\s*:|clip\s*:)",
    re.I,
)

# ========== PARCHE 2: Agregar #main-wrapper para DGCS ==========
# candidatos típicos de contenedor principal en sitios institucionales
MAIN_HINT_SELECTORS = [
    '[role="main"]', "main", "article", "#content", "#main", "#main-content",
    "#contenedor", "#contPrinc", ".contenido", "#content-core",
    "#main-wrapper",  # ← PARCHE 2: Específico para DGCS UNAM
]

def _parse(html: str) -> BeautifulSoup:
    try:
        return BeautifulSoup(html, "lxml")
    except Exception:
        return BeautifulSoup(html, "html.parser")

def _is_hidden(tag: Tag) -> bool:
    if not isinstance(tag, Tag):
        return False
    # atributos comunes
    if tag.has_attr("hidden") or tag.get("aria-hidden") == "true":
        return True
    # clases
    cls = tag.get("class") or []
    if any(c.lower() in HIDDEN_CLASS_HINTS for c in cls):
        return True
    # estilo inline
    style = tag.get("style") or ""
    if STYLE_HIDE_PAT.search(style):
        return True
    return False

def _unwrap_custom_elements(soup: BeautifulSoup) -> None:
    # Desenrolla elementos personalizados (<x-foo>) dejando su contenido
    changed = True
    while changed:
        changed = False
        for t in list(soup.find_all(True)):
            if not isinstance(t, Tag):
                continue
            name = t.name or ""
            if "-" in name and name not in {"script", "style"}:
                t.unwrap()
                changed = True

def _strip_noise(soup: BeautifulSoup) -> None:
    for bad in soup(["script", "style", "noscript", "template", "iframe"]):
        bad.decompose()
    
    # Quitar navegación/footers típicos
    for sel in ("nav", "footer", "aside"):
        for n in soup.select(sel):
            n.decompose()
    
    # ========== PARCHE 3: Quitar wrappers comunes de header/footer ==========
    for sel in ("#footer-wrapper", "#header-wrapper", ".footer", ".header"):
        elements = soup.select(sel)
        if elements:
            print(f"[DEBUG FILTERS] Removiendo {len(elements)} elementos con selector: {sel}")
        for n in elements:
            n.decompose()
    
    # Quitar nodos realmente ocultos, pero sin borrar sus padres
    hidden_count = 0
    for n in list(soup.find_all(_is_hidden)):
        n.decompose()
        hidden_count += 1
    if hidden_count > 0:
        print(f"[DEBUG FILTERS] Removidos {hidden_count} elementos ocultos")

def _score_container(tag: Tag) -> int:
    # Heurística simple: número de caracteres visibles dentro + bonus por <p>/<h>
    text_len = len(tag.get_text(" ", strip=True))
    p_count = len(tag.find_all("p"))
    h_count = sum(len(tag.find_all(h)) for h in ["h1", "h2", "h3"])
    score = text_len + 50 * p_count + 25 * h_count
    return score

def _pick_main_container(soup: BeautifulSoup) -> Tag:
    print(f"[DEBUG FILTERS] ========== SELECCIONANDO CONTENEDOR ==========")
    
    # Primero, intenta por selectores "amigos"
    candidates = []
    for sel in MAIN_HINT_SELECTORS:
        found = soup.select(sel)
        if found:
            print(f"[DEBUG FILTERS] Selector '{sel}' encontró {len(found)} elemento(s)")
            candidates.extend(found)
    
    # Si no hay, considera body
    if not candidates:
        print(f"[DEBUG FILTERS] ⚠️ Ningún selector específico funcionó, usando body")
        candidates = [soup.body or soup]

    # Selecciona el de mejor puntaje
    best = max(candidates, key=_score_container)
    best_score = _score_container(best)
    best_id = best.get('id') if best else None
    best_class = best.get('class') if best else None
    
    print(f"[DEBUG FILTERS] Contenedor seleccionado: <{best.name}>")
    print(f"[DEBUG FILTERS] ID: {best_id}")
    print(f"[DEBUG FILTERS] CLASS: {best_class}")
    print(f"[DEBUG FILTERS] Score: {best_score}")
    print(f"[DEBUG FILTERS] Chars: {len(best.get_text(' ', strip=True))}")
    print(f"[DEBUG FILTERS] ========================================\n")
    
    return best

def clean_html_and_pick(html: str) -> str:
    """
    Devuelve HTML del candidato principal YA limpiado.
    """
    soup = _parse(html)
    _unwrap_custom_elements(soup)          # 1) Unwrap Web Components
    _strip_noise(soup)                     # 2) Quitar ruido + ocultos
    root = _pick_main_container(soup)      # 3) Contenedor "amigo" genérico
    return str(root)
