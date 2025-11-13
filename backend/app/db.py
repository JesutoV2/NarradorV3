# Inserciones mínimas y estables a SQL Server (pyodbc)
import os, pyodbc
from urllib.parse import urlparse

_CONN_STR = os.getenv(
    "SNW_SQL_CONN",
    "Driver=ODBC Driver 18 for SQL Server;"
    "Server=(localdb)\\MSSQLLocalDB;"
    "Database=SeminarioNarrador;"
    "Trusted_Connection=yes;Encrypt=no;"
)

def _conn():
    return pyodbc.connect(_CONN_STR, autocommit=True)

def _exec(sql, params=()):
    with _conn() as cx:
        cur = cx.cursor()
        cur.execute(sql, params)
        try:
            rows = cur.fetchall()
            return rows
        except:
            return None

def upsert_page(url: str) -> int:
    netloc = urlparse(url).netloc.lower()
    domain = netloc.split(":")[0]
    # Crea si no existe
    _exec("""
        IF NOT EXISTS (SELECT 1 FROM snw.pages WHERE url = ?)
        INSERT INTO snw.pages(url, domain, site_name)
        VALUES(?, ?, ?);
    """, (url, url, domain, domain))
    # Devuelve id
    rows = _exec("SELECT TOP 1 page_id FROM snw.pages WHERE url = ? ORDER BY page_id DESC", (url,))
    return int(rows[0][0]) if rows else 0

def insert_run_and_metrics(
    run_id: str,
    page_id: int,
    url: str,
    n_chars: int,
    n_segments: int,
    t_extract_ms: int,
    t_normalize_ms: int,
    t_tts_ms: int,
    t_total_ms: int,
    duration_ms: int,
    ok: bool,
    err_msg: str | None,
) -> str:
    # RUN
    _exec("""
        INSERT INTO snw.runs(run_id, page_id, url, t_total_ms, ok, err_msg)
        VALUES(?, ?, ?, ?, ?, ?);
    """, (run_id, page_id, url, t_total_ms, 1 if ok else 0, err_msg))
    # METRICS (solo lo que sí tenemos)
    _exec("""
        INSERT INTO snw.metrics(run_id, n_chars, n_segments, t_extract_ms, t_normalize_ms, t_tts_ms, duration_ms)
        VALUES(?, ?, ?, ?, ?, ?, ?);
    """, (run_id, n_chars, n_segments, t_extract_ms, t_normalize_ms, t_tts_ms, duration_ms))
    return run_id

def register_asset(run_id: str, rel_path: str):
    _exec("""
        INSERT INTO snw.audio_assets(run_id, rel_path)
        VALUES(?, ?);
    """, (run_id, rel_path))
