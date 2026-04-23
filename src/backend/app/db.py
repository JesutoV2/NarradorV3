"""
Base de Datos Simplificada para NarradorWeb - VERSIÓN SQLITE
=============================================================
Versión: 2.0-SQLite
Fecha: Noviembre 13, 2025
Autor: Jorge Jesús Lee Soto

PROPÓSITO:
- Versión ALTERNATIVA usando SQLite (no requiere pyodbc ni SQL Server)
- Útil para desarrollo y pruebas cuando SQL Server no está disponible
- 100% compatible con la API de db_v2.py

VENTAJAS DE SQLITE:
- ✅ No requiere instalar pyodbc (viene con Python)
- ✅ No requiere SQL Server
- ✅ Base de datos en un solo archivo .db
- ✅ Perfecta para desarrollo y pruebas
- ✅ Fácil de hacer backup (copiar archivo)

DESVENTAJAS:
- ❌ No es SQL Server (para producción se recomienda SQL Server)
- ❌ Menos robusto para concurrencia alta

INSTALACIÓN:
  No requiere instalación, SQLite viene incluido con Python

USO:
  import db_sqlite as db
  # Usar exactamente igual que db_v2.py
"""

from __future__ import annotations
import os
import sqlite3
import logging
from typing import Optional
from urllib.parse import urlparse
import sys
from pathlib import Path

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Ajuste de ruta para compatibilidad con PyInstaller
if getattr(sys, 'frozen', False):
    # Si corre como ejecutable, la BD va junto al .exe
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent

DEFAULT_DB_PATH = BASE_DIR / "seminario_narrador.db"
DB_PATH = os.getenv("SNW_SQLITE_DB", str(DEFAULT_DB_PATH))

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def _get_connection():
    """
    Crea conexión a SQLite.
    
    Returns:
        sqlite3.Connection: Conexión activa
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
        return conn
    except Exception as exc:
        logging.error(f"Error conectando a SQLite: {exc}")
        raise RuntimeError(f"No se pudo conectar a la base de datos: {exc}")


def _execute(sql: str, params: tuple = (), fetch: bool = True) -> Optional[list]:
    """
    Ejecuta una query SQL y devuelve resultados si aplica.
    
    Args:
        sql: Query SQL (usar ? para parámetros)
        params: Tupla con valores de parámetros
        fetch: Si debe intentar hacer fetchall()
    
    Returns:
        Lista de filas si la query devuelve datos, None si no
    """
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        
        if fetch:
            try:
                rows = cursor.fetchall()
                return rows
            except:
                return None
        return None
    except Exception as exc:
        logging.error(f"Error ejecutando SQL: {exc}")
        logging.debug(f"SQL: {sql}")
        logging.debug(f"Params: {params}")
        raise
    finally:
        conn.close()


def init_db():
    """
    Inicializa el esquema de la base de datos SQLite.
    Llamar esto UNA VEZ al inicio si la BD no existe.
    """
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        
        # Tabla pages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pages (
                page_id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                domain TEXT NOT NULL,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pages_domain ON pages(domain)")
        
        # Tabla runs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                page_id INTEGER NOT NULL,
                url TEXT,
                ttcu_seconds REAL NOT NULL,
                ptnn_percent REAL NOT NULL,
                total_time_ms INTEGER NOT NULL,
                audio_duration_ms INTEGER,
                chars_original INTEGER NOT NULL,
                chars_extracted INTEGER NOT NULL,
                ok INTEGER DEFAULT 1,
                err_msg TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (page_id) REFERENCES pages(page_id)
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_created ON runs(created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_ttcu ON runs(ttcu_seconds)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_ptnn ON runs(ptnn_percent)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_page ON runs(page_id)")
        
        # Tabla audio_files
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audio_files (
                audio_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                size_bytes INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (run_id) REFERENCES runs(run_id)
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audio_run ON audio_files(run_id)")
        
        conn.commit()
        logging.info(f"✅ Base de datos SQLite inicializada: {DB_PATH}")
    except Exception as exc:
        logging.error(f"Error inicializando BD: {exc}")
        raise
    finally:
        conn.close()


# ============================================================================
# FUNCIONES PRINCIPALES (API IDÉNTICA A db_v2.py)
# ============================================================================

def upsert_page(url: str, title: Optional[str] = None) -> int:
    """
    Inserta una página si no existe, o la recupera si ya existe.
    
    Args:
        url: URL completa de la página procesada
        title: Título de la página (opcional)
    
    Returns:
        page_id: ID de la página (int)
    """
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    # Primero verificar si ya existe
    rows = _execute("SELECT page_id FROM pages WHERE url = ?", (url,))
    
    if rows:
        # Ya existe, devolver el page_id existente
        return int(rows[0]['page_id'])
    
    # No existe, insertar
    try:
        _execute(
            "INSERT INTO pages (url, domain, title) VALUES (?, ?, ?)",
            (url, domain, title),
            fetch=False
        )
    except sqlite3.IntegrityError:
        # Race condition: otro proceso insertó entre SELECT e INSERT
        # Intentar SELECT nuevamente
        rows = _execute("SELECT page_id FROM pages WHERE url = ?", (url,))
        if rows:
            return int(rows[0]['page_id'])
        raise RuntimeError(f"Race condition al insertar URL: {url}")
    
    # Recuperar page_id del registro recién insertado
    rows = _execute("SELECT page_id FROM pages WHERE url = ?", (url,))
    
    if not rows:
        raise RuntimeError(f"No se pudo obtener page_id para URL: {url}")
    
    return int(rows[0]['page_id'])


def insert_run(
    run_id: str,
    page_id: int,
    url: str,
    ttcu_seconds: float,
    ptnn_percent: float,
    total_time_ms: int,
    audio_duration_ms: Optional[int],
    chars_original: int,
    chars_extracted: int,
    ok: bool = True,
    err_msg: Optional[str] = None,
) -> None:
    """
    Registra una ejecución del sistema con sus métricas.
    
    API IDÉNTICA a db_v2.py para compatibilidad.
    """
    _execute(
        """
        INSERT INTO runs (
            run_id, page_id, url,
            ttcu_seconds, ptnn_percent,
            total_time_ms, audio_duration_ms,
            chars_original, chars_extracted,
            ok, err_msg
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id, page_id, url,
            ttcu_seconds, ptnn_percent,
            total_time_ms, audio_duration_ms,
            chars_original, chars_extracted,
            1 if ok else 0, err_msg
        ),
        fetch=False
    )
    
    logging.info(
        f"Run registrado: {run_id[:8]}... | "
        f"TTCU: {ttcu_seconds:.2f}s | "
        f"PTNN: {ptnn_percent:.1f}%"
    )


def register_audio_file(
    run_id: str,
    file_path: str,
    size_bytes: Optional[int] = None
) -> None:
    """
    Registra el archivo de audio generado.
    """
    _execute(
        "INSERT INTO audio_files (run_id, file_path, size_bytes) VALUES (?, ?, ?)",
        (run_id, file_path, size_bytes),
        fetch=False
    )


# ============================================================================
# FUNCIONES DE CONSULTA
# ============================================================================

def get_stats() -> dict:
    """
    Obtiene estadísticas generales del sistema.
    """
    rows = _execute(
        """
        SELECT 
            COUNT(*) as total_runs,
            AVG(ttcu_seconds) as avg_ttcu,
            AVG(ptnn_percent) as avg_ptnn,
            SUM(CASE WHEN ok = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
        FROM runs
        """
    )
    
    if not rows:
        return {
            "total_runs": 0,
            "avg_ttcu": 0.0,
            "avg_ptnn": 0.0,
            "success_rate": 0.0
        }
    
    row = rows[0]
    return {
        "total_runs": row['total_runs'],
        "avg_ttcu": float(row['avg_ttcu']) if row['avg_ttcu'] else 0.0,
        "avg_ptnn": float(row['avg_ptnn']) if row['avg_ptnn'] else 0.0,
        "success_rate": float(row['success_rate']) if row['success_rate'] else 0.0
    }


def get_runs_by_domain() -> list[dict]:
    """
    Obtiene métricas agrupadas por dominio.
    """
    rows = _execute(
        """
        SELECT 
            p.domain,
            COUNT(*) as run_count,
            AVG(r.ttcu_seconds) as avg_ttcu,
            AVG(r.ptnn_percent) as avg_ptnn
        FROM runs r
        JOIN pages p ON r.page_id = p.page_id
        WHERE r.ok = 1
        GROUP BY p.domain
        ORDER BY run_count DESC
        """
    )
    
    if not rows:
        return []
    
    return [
        {
            "domain": row['domain'],
            "count": row['run_count'],
            "avg_ttcu": float(row['avg_ttcu']),
            "avg_ptnn": float(row['avg_ptnn'])
        }
        for row in rows
    ]


# ============================================================================
# INICIALIZACIÓN AUTOMÁTICA
# ============================================================================

# Inicializar BD automáticamente al importar el módulo
try:
    init_db()
except Exception as e:
    logging.warning(f"No se pudo inicializar BD SQLite: {e}")


# ============================================================================
# SCRIPT DE PRUEBA
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("TEST DE BASE DE DATOS SQLITE")
    print("=" * 60)
    print(f"📁 Archivo de BD: {DB_PATH}")
    print()
    
    try:
        # Inicializar BD
        print("[0/4] Inicializando base de datos...")
        init_db()
        print("✅ BD inicializada")
        
        # Test 1: Insertar página
        print("\n[1/4] Insertando página de prueba...")
        page_id = upsert_page(
            url="https://es.wikipedia.org/wiki/Python",
            title="Python - Wikipedia"
        )
        print(f"✅ Page ID: {page_id}")
        
        # Test 2: Insertar run
        print("\n[2/4] Insertando ejecución de prueba...")
        import uuid
        test_run_id = uuid.uuid4().hex
        
        insert_run(
            run_id=test_run_id,
            page_id=page_id,
            url="https://es.wikipedia.org/wiki/Python",
            ttcu_seconds=1.234,
            ptnn_percent=85.5,
            total_time_ms=1500,
            audio_duration_ms=12000,
            chars_original=5000,
            chars_extracted=725
        )
        print(f"✅ Run ID: {test_run_id[:8]}...")
        
        # Test 3: Obtener estadísticas
        print("\n[3/4] Obteniendo estadísticas...")
        stats = get_stats()
        print(f"✅ Total runs: {stats['total_runs']}")
        print(f"✅ TTCU promedio: {stats['avg_ttcu']:.2f}s")
        print(f"✅ PTNN promedio: {stats['avg_ptnn']:.1f}%")
        
        # Test 4: Stats por dominio
        print("\n[4/4] Métricas por dominio...")
        domains = get_runs_by_domain()
        for d in domains:
            print(f"✅ {d['domain']}: {d['count']} runs, TTCU={d['avg_ttcu']:.2f}s")
        
        print("\n" + "=" * 60)
        print("✅ TODOS LOS TESTS PASARON")
        print("=" * 60)
        print()
        print("📌 NOTA: Esta es la versión SQLite.")
        print("   Para usar SQL Server, resolver el problema de pyodbc primero.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
