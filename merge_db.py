#!/usr/bin/env python3
"""
Script de Fusión de Bases de Datos SQLite para Narrador Web
===========================================================
Versión: 1.0
Fecha: Noviembre 2025
Autor: Jorge Jesús Lee Soto (con asistencia de IA)

PROPÓSITO:
- Fusionar los datos de una base de datos de prueba (fuente)
  en la base de datos principal (maestra).
- Maneja correctamente las claves primarias y foráneas para evitar conflictos.

USO:
1. Copia el archivo `seminario_narrador.db` de la computadora de prueba
   a la raíz de este proyecto. Puedes renombrarlo (ej. `test_pc.db`).
2. Ejecuta el script desde la terminal:
   
   python merge_db.py RUTA_A_DB_FUENTE

EJEMPLO:
   python merge_db.py test_pc.db
"""

import sqlite3
import sys
from pathlib import Path

# La base de datos maestra siempre está en la misma ubicación
MASTER_DB_PATH = Path(__file__).parent / "src" / "backend" / "seminario_narrador.db"

def merge_databases(source_db_path: Path):
    if not source_db_path.exists():
        print(f"❌ ERROR: El archivo de base de datos fuente no existe en: {source_db_path}")
        return

    if not MASTER_DB_PATH.exists():
        print(f"❌ ERROR: No se encontró la base de datos maestra en: {MASTER_DB_PATH}")
        print("   Asegúrate de que la base de datos principal exista.")
        return

    print(f"🔗 Conectando a la base de datos maestra: {MASTER_DB_PATH}")
    conn = sqlite3.connect(MASTER_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        print(f"📎 Adjuntando base de datos fuente: {source_db_path}")
        cursor.execute(f"ATTACH DATABASE '{source_db_path.resolve()}' AS source_db")

        # --- 1. Fusionar la tabla 'pages' ---
        # Esta es la parte más compleja debido a las claves autoincrementales.
        # No podemos copiar page_id directamente.
        print("\n[1/3] 📄 Fusionando tabla 'pages'...")
        
        cursor.execute("SELECT url FROM source_db.pages")
        source_pages = cursor.fetchall()
        
        # Usamos INSERT OR IGNORE para insertar solo las URLs que no existen.
        pages_to_insert = [(row['url'],) for row in source_pages]
        cursor.executemany("INSERT OR IGNORE INTO main.pages (url, domain) SELECT url, domain FROM source_db.pages WHERE url = ?", pages_to_insert)
        conn.commit()
        print(f"   - Se procesaron {len(source_pages)} páginas de la fuente.")

        # --- 2. Crear un mapa de page_id (antiguo -> nuevo) ---
        # Necesitamos saber qué page_id corresponde a cada URL en la BD maestra.
        page_id_map = {}
        cursor.execute("SELECT page_id, url FROM source_db.pages")
        for row in cursor.fetchall():
            cursor.execute("SELECT page_id FROM main.pages WHERE url = ?", (row['url'],))
            master_page_row = cursor.fetchone()
            if master_page_row:
                page_id_map[row['page_id']] = master_page_row['page_id']

        # --- 3. Fusionar la tabla 'runs' ---
        print("\n[2/3] 🚀 Fusionando tabla 'runs'...")
        cursor.execute("SELECT * FROM source_db.runs")
        source_runs = cursor.fetchall()
        
        runs_to_insert = []
        for run in source_runs:
            old_page_id = run['page_id']
            new_page_id = page_id_map.get(old_page_id)
            if new_page_id is None:
                print(f"   - ⚠️  Advertencia: No se encontró mapeo para page_id {old_page_id}. Saltando run {run['run_id'][:8]}...")
                continue
            
            runs_to_insert.append((
                run['run_id'], new_page_id, run['url'], run['ttcu_seconds'],
                run['ptnn_percent'], run['total_time_ms'], run['audio_duration_ms'],
                run['chars_original'], run['chars_extracted'], run['ok'], run['err_msg']
            ))

        # Usamos INSERT OR IGNORE para no fallar si un run_id ya existe (muy improbable con UUIDs)
        cursor.executemany("""
            INSERT OR IGNORE INTO main.runs (
                run_id, page_id, url, ttcu_seconds, ptnn_percent, total_time_ms,
                audio_duration_ms, chars_original, chars_extracted, ok, err_msg
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, runs_to_insert)
        conn.commit()
        print(f"   - Se procesaron {len(source_runs)} ejecuciones de la fuente.")
        print(f"   - Se insertaron {cursor.rowcount} nuevas ejecuciones.")

        # --- 4. Fusionar 'audio_files' (opcional, pero bueno tenerlo) ---
        print("\n[3/3] 🔊 Fusionando tabla 'audio_files'...")
        cursor.execute("INSERT OR IGNORE INTO main.audio_files SELECT * FROM source_db.audio_files")
        conn.commit()
        print(f"   - Se insertaron {cursor.rowcount} registros de audio.")

        print("\n✅ ¡Fusión completada exitosamente!")

    except Exception as e:
        print(f"\n❌ ERROR durante la fusión: {e}")
        conn.rollback()
    finally:
        print("🔚 Desvinculando base de datos fuente.")
        cursor.execute("DETACH DATABASE source_db")
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python merge_db.py <ruta_al_archivo_db_fuente>")
        print("Ejemplo: python merge_db.py test_pc.db")
        sys.exit(1)

    source_file = Path(sys.argv[1])
    merge_databases(source_file)