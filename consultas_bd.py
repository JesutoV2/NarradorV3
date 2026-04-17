#!/usr/bin/env python3
"""
Script de Consultas para Base de Datos del Narrador Web
========================================================
Versión: 1.0
Fecha: Noviembre 13, 2025
Autor: Jorge Jesús Lee Soto

USO:
    python consultas_bd.py

OPCIONES:
    1. Ver estadísticas generales
    2. Ver todos los registros
    3. Ver registros por dominio
    4. Ver últimos 10 registros
    5. Ver páginas procesadas
    6. Exportar a CSV
    7. Salir
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime

# Ruta de la base de datos
DB_PATH = Path(__file__).parent / "src" / "backend" / "seminario_narrador.db"

def conectar():
    """Conecta a la base de datos SQLite."""
    if not DB_PATH.exists():
        print(f"❌ ERROR: No se encontró la base de datos en: {DB_PATH}")
        print("   Asegúrate de estar en el directorio raíz del proyecto.")
        return None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ ERROR conectando a BD: {e}")
        return None


def estadisticas_generales():
    """Muestra estadísticas generales del sistema."""
    conn = conectar()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Estadísticas principales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_runs,
                AVG(ttcu_seconds) as avg_ttcu,
                AVG(ptnn_percent) as avg_ptnn,
                MIN(ttcu_seconds) as min_ttcu,
                MAX(ttcu_seconds) as max_ttcu,
                MIN(ptnn_percent) as min_ptnn,
                MAX(ptnn_percent) as max_ptnn,
                SUM(CASE WHEN ok = 1 THEN 1 ELSE 0 END) as exitosos,
                SUM(CASE WHEN ok = 0 THEN 1 ELSE 0 END) as fallidos
            FROM runs
        """)
        
        row = cursor.fetchone()
        
        print("\n" + "=" * 70)
        print("📊 ESTADÍSTICAS GENERALES")
        print("=" * 70)
        print(f"Total de ejecuciones:       {row['total_runs']}")
        print(f"Ejecuciones exitosas:       {row['exitosos']}")
        print(f"Ejecuciones fallidas:       {row['fallidos']}")
        print(f"Tasa de éxito:              {(row['exitosos'] / row['total_runs'] * 100):.1f}%" if row['total_runs'] > 0 else "N/A")
        print()
        print(f"TTCU promedio:              {row['avg_ttcu']:.3f} segundos")
        print(f"TTCU mínimo:                {row['min_ttcu']:.3f} segundos")
        print(f"TTCU máximo:                {row['max_ttcu']:.3f} segundos")
        print()
        print(f"PTNN promedio:              {row['avg_ptnn']:.1f}%")
        print(f"PTNN mínimo:                {row['min_ptnn']:.1f}%")
        print(f"PTNN máximo:                {row['max_ptnn']:.1f}%")
        print("=" * 70)
        
        # Contar páginas
        cursor.execute("SELECT COUNT(*) as total FROM pages")
        total_pages = cursor.fetchone()['total']
        print(f"Total de páginas únicas:    {total_pages}")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()


def ver_todos_registros():
    """Muestra todos los registros de runs."""
    conn = conectar()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                r.run_id,
                p.domain,
                r.url,
                r.ttcu_seconds,
                r.ptnn_percent,
                r.chars_original,
                r.chars_extracted,
                r.ok,
                r.created_at
            FROM runs r
            JOIN pages p ON r.page_id = p.page_id
            ORDER BY r.created_at DESC
        """)
        
        rows = cursor.fetchall()
        
        print("\n" + "=" * 150)
        print("📋 TODOS LOS REGISTROS")
        print("=" * 150)
        print(f"{'Run ID':<10} | {'Dominio':<25} | {'TTCU (s)':<8} | {'PTNN (%)':<8} | {'Chars':<12} | {'Estado':<7} | {'Fecha':<19}")
        print("-" * 150)
        
        for row in rows:
            run_id = row['run_id'][:8]
            domain = row['domain'][:25]
            ttcu = row['ttcu_seconds']
            ptnn = row['ptnn_percent']
            chars = f"{row['chars_extracted']}/{row['chars_original']}"
            estado = "✅ OK" if row['ok'] else "❌ FAIL"
            fecha = row['created_at'][:19]
            
            print(f"{run_id:<10} | {domain:<25} | {ttcu:>8.2f} | {ptnn:>8.1f} | {chars:<12} | {estado:<7} | {fecha}")
        
        print("=" * 150)
        print(f"Total: {len(rows)} registros\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()


def registros_por_dominio():
    """Muestra métricas agrupadas por dominio."""
    conn = conectar()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.domain,
                COUNT(*) as runs,
                AVG(r.ttcu_seconds) as avg_ttcu,
                AVG(r.ptnn_percent) as avg_ptnn,
                MIN(r.ttcu_seconds) as min_ttcu,
                MAX(r.ttcu_seconds) as max_ttcu
            FROM runs r
            JOIN pages p ON r.page_id = p.page_id
            WHERE r.ok = 1
            GROUP BY p.domain
            ORDER BY runs DESC, avg_ttcu ASC
        """)
        
        rows = cursor.fetchall()
        
        print("\n" + "=" * 100)
        print("🌐 MÉTRICAS POR DOMINIO")
        print("=" * 100)
        print(f"{'Dominio':<35} | {'Runs':<5} | {'TTCU Prom':<10} | {'TTCU Min':<10} | {'TTCU Max':<10} | {'PTNN Prom':<10}")
        print("-" * 100)
        
        for row in rows:
            domain = row['domain'][:35]
            runs = row['runs']
            avg_ttcu = row['avg_ttcu']
            min_ttcu = row['min_ttcu']
            max_ttcu = row['max_ttcu']
            avg_ptnn = row['avg_ptnn']
            
            print(f"{domain:<35} | {runs:<5} | {avg_ttcu:>10.2f}s | {min_ttcu:>10.2f}s | {max_ttcu:>10.2f}s | {avg_ptnn:>9.1f}%")
        
        print("=" * 100)
        print(f"Total dominios: {len(rows)}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()


def ultimos_registros(limite=10):
    """Muestra los últimos N registros."""
    conn = conectar()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                r.run_id,
                p.domain,
                r.ttcu_seconds,
                r.ptnn_percent,
                r.ok,
                r.created_at
            FROM runs r
            JOIN pages p ON r.page_id = p.page_id
            ORDER BY r.created_at DESC
            LIMIT ?
        """, (limite,))
        
        rows = cursor.fetchall()
        
        print("\n" + "=" * 100)
        print(f"📅 ÚLTIMOS {limite} REGISTROS")
        print("=" * 100)
        print(f"{'Run ID':<10} | {'Dominio':<30} | {'TTCU (s)':<8} | {'PTNN (%)':<8} | {'Estado':<7} | {'Fecha':<19}")
        print("-" * 100)
        
        for row in rows:
            run_id = row['run_id'][:8]
            domain = row['domain'][:30]
            ttcu = row['ttcu_seconds']
            ptnn = row['ptnn_percent']
            estado = "✅" if row['ok'] else "❌"
            fecha = row['created_at'][:19]
            
            print(f"{run_id:<10} | {domain:<30} | {ttcu:>8.2f} | {ptnn:>8.1f} | {estado:<7} | {fecha}")
        
        print("=" * 100 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()


def ver_paginas():
    """Muestra todas las páginas procesadas."""
    conn = conectar()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.page_id,
                p.domain,
                p.url,
                COUNT(r.run_id) as veces_procesada,
                p.created_at
            FROM pages p
            LEFT JOIN runs r ON p.page_id = r.page_id
            GROUP BY p.page_id
            ORDER BY veces_procesada DESC, p.created_at DESC
        """)
        
        rows = cursor.fetchall()
        
        print("\n" + "=" * 120)
        print("📄 PÁGINAS PROCESADAS")
        print("=" * 120)
        print(f"{'ID':<5} | {'Dominio':<30} | {'URL':<50} | {'Veces':<6} | {'Primera vez':<19}")
        print("-" * 120)
        
        for row in rows:
            page_id = row['page_id']
            domain = row['domain'][:30]
            url = row['url'][:50]
            veces = row['veces_procesada']
            fecha = row['created_at'][:19]
            
            print(f"{page_id:<5} | {domain:<30} | {url:<50} | {veces:<6} | {fecha}")
        
        print("=" * 120)
        print(f"Total páginas: {len(rows)}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()


def exportar_csv():
    """Exporta todos los datos a un archivo CSV."""
    conn = conectar()
    if not conn:
        return
    
    try:
        import csv
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                r.run_id,
                p.domain,
                r.url,
                r.ttcu_seconds,
                r.ptnn_percent,
                r.total_time_ms,
                r.audio_duration_ms,
                r.chars_original,
                r.chars_extracted,
                r.ok,
                r.err_msg,
                r.created_at
            FROM runs r
            JOIN pages p ON r.page_id = p.page_id
            ORDER BY r.created_at DESC
        """)
        
        rows = cursor.fetchall()
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"narrador_datos_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'run_id', 'domain', 'url', 'ttcu_seconds', 'ptnn_percent',
                'total_time_ms', 'audio_duration_ms', 'chars_original',
                'chars_extracted', 'ok', 'err_msg', 'created_at'
            ])
            
            # Data
            for row in rows:
                writer.writerow([
                    row['run_id'], row['domain'], row['url'],
                    row['ttcu_seconds'], row['ptnn_percent'],
                    row['total_time_ms'], row['audio_duration_ms'],
                    row['chars_original'], row['chars_extracted'],
                    row['ok'], row['err_msg'], row['created_at']
                ])
        
        print(f"\n✅ Datos exportados exitosamente a: {filename}")
        print(f"   Total de registros: {len(rows)}\n")
        
    except Exception as e:
        print(f"❌ Error exportando: {e}")
    finally:
        conn.close()


def menu_principal():
    """Muestra el menú principal."""
    while True:
        print("\n" + "=" * 70)
        print("🗄️  CONSULTAS BASE DE DATOS - NARRADOR WEB")
        print("=" * 70)
        print("1. Ver estadísticas generales")
        print("2. Ver todos los registros")
        print("3. Ver registros por dominio")
        print("4. Ver últimos 10 registros")
        print("5. Ver páginas procesadas")
        print("6. Exportar datos a CSV")
        print("7. Salir")
        print("=" * 70)
        
        opcion = input("\nSelecciona una opción (1-7): ").strip()
        
        if opcion == "1":
            estadisticas_generales()
        elif opcion == "2":
            ver_todos_registros()
        elif opcion == "3":
            registros_por_dominio()
        elif opcion == "4":
            ultimos_registros(10)
        elif opcion == "5":
            ver_paginas()
        elif opcion == "6":
            exportar_csv()
        elif opcion == "7":
            print("\n👋 ¡Hasta luego!\n")
            break
        else:
            print("\n❌ Opción inválida. Intenta de nuevo.")
        
        input("\nPresiona ENTER para continuar...")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 SCRIPT DE CONSULTAS - NARRADOR WEB")
    print("=" * 70)
    print(f"Base de datos: {DB_PATH}")
    print("=" * 70)
    
    if not DB_PATH.exists():
        print(f"\n❌ ERROR: No se encontró la base de datos.")
        print(f"   Ruta esperada: {DB_PATH}")
        print(f"   Asegúrate de ejecutar este script desde el directorio raíz del proyecto.\n")
    else:
        print(f"✅ Base de datos encontrada\n")
        menu_principal()
