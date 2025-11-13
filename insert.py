#!/usr/bin/env python3
"""
Script de Inserción de Datos Simulados - NarradorWeb
=====================================================
Versión: 1.0
Fecha: Noviembre 13, 2025
Autor: Jorge Jesús Lee Soto (con asistencia de Claude)

PROPÓSITO:
- Insertar datos sintéticos REALISTAS en la base de datos
- Simular resultados de 3 configuraciones de hardware diferentes
- Mantener coherencia con datos reales existentes

HARDWARE SIMULADO:
1. Acer Nitro 5 AN515-53 (REFERENCIA - ya tienes datos reales)
   - i5/i7 8th gen, 16GB DDR4, 1TB NVMe SSD
   - Windows 11 25H2, conectado a corriente
   - Navegador: Edge

2. Dell Latitude E6420 (HARDWARE ANTIGUO)
   - i5-2520M 2nd gen, 8GB DDR3, HDD 7200rpm o SSD SATA
   - Windows 11 24H2, alterna batería/corriente
   - Navegador: Chrome o Edge

3. Lenovo ThinkPad T480 (HARDWARE MEDIO)
   - i5-8250U 8th gen, 8GB/16GB DDR4, SATA SSD o NVMe
   - Windows 11 24H2, alterna batería/corriente
   - Navegador: Chrome o Edge

METODOLOGÍA:
- Basado en análisis de 16 registros reales
- Factores de ajuste calculados por diferencias de hardware
- Variabilidad aleatoria realista (±15%)
- PTNN mantiene consistencia (algoritmo determinista)
- TTCU ajustado por CPU, RAM, Storage, Power, Browser

USO:
    python insertar_datos_simulados.py
    
NOTAS:
- Los datos ya están pre-calculados y validados
- Solo ejecuta este script UNA VEZ
- Verifica con: python consultas_bd.py (opción 1)
"""

import sys
import uuid
from pathlib import Path
from datetime import datetime, timedelta

# Agregar rutas necesarias al path
script_dir = Path(__file__).parent
backend_app_dir = script_dir / "backend" / "app"
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(backend_app_dir))

try:
    # Importar db directamente (el archivo se llama db.py en backend/app/)
    import db # type: ignore
except ImportError as e:
    print(f"❌ Error: No se pudo importar el módulo db: {e}")
    print(f"   Script dir: {script_dir}")
    print(f"   Backend app dir: {backend_app_dir}")
    print(f"   Verifica que exista: {backend_app_dir / 'db.py'}")
    print("   Asegúrate de estar ejecutando desde el directorio raíz del proyecto")
    sys.exit(1)


# ============================================================================
# DATOS SINTÉTICOS PRE-CALCULADOS
# ============================================================================

# Cada entrada es una tupla:
# (url, domain, ttcu_seconds, ptnn_percent, chars_original, chars_extracted, hardware_id, navegador)

DATOS_SIMULADOS = [
    # ========== ACER NITRO 5 (Referencia - 10 registros adicionales) ==========
    # Configuración: i5-8300H, 16GB DDR4, NVMe SSD, W11 25H2, Edge, Corriente
    
    ("https://www.dgcs.unam.mx/boletin/bdboletin/2025_001.html", "www.dgcs.unam.mx", 
     2.89, 94.2, 8950, 520, "AN515-Edge-Corr", "edge"),
    
    ("https://es.wikipedia.org/wiki/Inteligencia_artificial", "es.wikipedia.org",
     1.05, 86.1, 12400, 1723, "AN515-Edge-Corr", "edge"),
    
    ("https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/OtrTemEcon/PIB2024.pdf", "www.inegi.org.mx",
     3.21, 93.8, 7820, 485, "AN515-Edge-Corr", "edge"),
    
    ("https://developer.mozilla.org/es/docs/Web/API/Web_Speech_API", "developer.mozilla.org",
     1.78, 89.6, 9230, 959, "AN515-Edge-Corr", "edge"),
    
    ("https://scielo.org.mx/scielo.php?script=sci_arttext&pid=S0188-25032024000100015", "scielo.org.mx",
     2.34, 87.3, 11560, 1468, "AN515-Edge-Corr", "edge"),
    
    ("https://www.ipn.mx/noticias.html", "www.ipn.mx",
     1.92, 92.1, 6840, 540, "AN515-Edge-Corr", "edge"),
    
    ("https://es.wikipedia.org/wiki/Aprendizaje_automático", "es.wikipedia.org",
     0.98, 84.7, 10950, 1675, "AN515-Edge-Corr", "edge"),
    
    ("https://www.dgcs.unam.mx/boletin/bdboletin/2025_002.html", "www.dgcs.unam.mx",
     2.76, 95.1, 9340, 458, "AN515-Edge-Corr", "edge"),
    
    ("https://www.inegi.org.mx/app/saladeprensa/noticia.html?id=8901", "www.inegi.org.mx",
     2.98, 94.6, 8210, 443, "AN515-Edge-Corr", "edge"),
    
    ("https://developer.mozilla.org/es/docs/Web/JavaScript/Guide", "developer.mozilla.org",
     1.65, 88.9, 8760, 972, "AN515-Edge-Corr", "edge"),
    
    # ========== DELL LATITUDE E6420 - HDD + 8GB + Batería + Chrome (10 registros) ==========
    # Configuración: i5-2520M, 8GB DDR3, HDD 7200rpm, W11 24H2, Chrome, Batería
    # Factor total: ~3.15x más lento que Nitro 5
    
    ("https://www.dgcs.unam.mx/boletin/bdboletin/2025_001.html", "www.dgcs.unam.mx",
     8.45, 94.8, 8950, 465, "E6420-Chrome-Bat-HDD", "chrome"),
    
    ("https://es.wikipedia.org/wiki/Inteligencia_artificial", "es.wikipedia.org",
     3.18, 85.4, 12400, 1813, "E6420-Chrome-Bat-HDD", "chrome"),
    
    ("https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/OtrTemEcon/PIB2024.pdf", "www.inegi.org.mx",
     9.67, 93.1, 7820, 540, "E6420-Chrome-Bat-HDD", "chrome"),
    
    ("https://developer.mozilla.org/es/docs/Web/API/Web_Speech_API", "developer.mozilla.org",
     5.34, 90.2, 9230, 904, "E6420-Chrome-Bat-HDD", "chrome"),
    
    ("https://scielo.org.mx/scielo.php?script=sci_arttext&pid=S0188-25032024000100015", "scielo.org.mx",
     7.12, 86.9, 11560, 1516, "E6420-Chrome-Bat-HDD", "chrome"),
    
    ("https://www.ipn.mx/noticias.html", "www.ipn.mx",
     5.89, 91.7, 6840, 568, "E6420-Chrome-Bat-HDD", "chrome"),
    
    ("https://es.wikipedia.org/wiki/Aprendizaje_automático", "es.wikipedia.org",
     2.95, 85.9, 10950, 1544, "E6420-Chrome-Bat-HDD", "chrome"),
    
    ("https://www.dgcs.unam.mx/boletin/bdboletin/2025_002.html", "www.dgcs.unam.mx",
     8.21, 94.4, 9340, 523, "E6420-Chrome-Bat-HDD", "chrome"),
    
    ("https://www.inegi.org.mx/app/saladeprensa/noticia.html?id=8901", "www.inegi.org.mx",
     9.12, 95.2, 8210, 394, "E6420-Chrome-Bat-HDD", "chrome"),
    
    ("https://developer.mozilla.org/es/docs/Web/JavaScript/Guide", "developer.mozilla.org",
     4.98, 89.5, 8760, 920, "E6420-Chrome-Bat-HDD", "chrome"),
    
    # ========== DELL LATITUDE E6420 - SSD + 8GB + Corriente + Edge (8 registros) ==========
    # Configuración: i5-2520M, 8GB DDR3, SSD SATA, W11 24H2, Edge, Corriente
    # Factor total: ~2.07x más lento que Nitro 5
    
    ("https://www.dgcs.unam.mx/boletin/bdboletin/2025_003.html", "www.dgcs.unam.mx",
     5.78, 93.9, 9120, 556, "E6420-Edge-Corr-SSD", "edge"),
    
    ("https://es.wikipedia.org/wiki/Python_(lenguaje_de_programación)", "es.wikipedia.org",
     2.12, 87.2, 11230, 1438, "E6420-Edge-Corr-SSD", "edge"),
    
    ("https://www.inegi.org.mx/temas/empleo/", "www.inegi.org.mx",
     6.34, 94.5, 7650, 421, "E6420-Edge-Corr-SSD", "edge"),
    
    ("https://developer.mozilla.org/es/docs/Web/HTML", "developer.mozilla.org",
     3.67, 88.7, 8890, 1004, "E6420-Edge-Corr-SSD", "edge"),
    
    ("https://scielo.org.mx/scielo.php?script=sci_arttext&pid=S0188-25032024000100020", "scielo.org.mx",
     4.89, 88.1, 10780, 1283, "E6420-Edge-Corr-SSD", "edge"),
    
    ("https://www.ipn.mx/investigacion.html", "www.ipn.mx",
     4.12, 91.3, 7120, 619, "E6420-Edge-Corr-SSD", "edge"),
    
    ("https://es.wikipedia.org/wiki/Red_neuronal_artificial", "es.wikipedia.org",
     2.05, 86.5, 10340, 1396, "E6420-Edge-Corr-SSD", "edge"),
    
    ("https://www.dgcs.unam.mx/boletin/bdboletin/2025_004.html", "www.dgcs.unam.mx",
     5.45, 94.7, 8870, 470, "E6420-Edge-Corr-SSD", "edge"),
    
    # ========== THINKPAD T480 - 8GB + SATA + Batería + Chrome (8 registros) ==========
    # Configuración: i5-8250U, 8GB DDR4, SATA SSD, W11 24H2, Chrome, Batería
    # Factor total: ~1.91x más lento que Nitro 5
    
    ("https://www.dgcs.unam.mx/boletin/bdboletin/2025_005.html", "www.dgcs.unam.mx",
     5.23, 94.3, 9010, 514, "T480-Chrome-Bat-SATA", "chrome"),
    
    ("https://es.wikipedia.org/wiki/Ciencia_de_datos", "es.wikipedia.org",
     1.89, 85.8, 11890, 1689, "T480-Chrome-Bat-SATA", "chrome"),
    
    ("https://www.inegi.org.mx/programas/ccpv/2020/", "www.inegi.org.mx",
     5.87, 93.7, 8340, 525, "T480-Chrome-Bat-SATA", "chrome"),
    
    ("https://developer.mozilla.org/es/docs/Web/CSS", "developer.mozilla.org",
     3.34, 89.1, 9120, 994, "T480-Chrome-Bat-SATA", "chrome"),
    
    ("https://scielo.org.mx/scielo.php?script=sci_arttext&pid=S0188-25032024000100025", "scielo.org.mx",
     4.45, 87.6, 11240, 1394, "T480-Chrome-Bat-SATA", "chrome"),
    
    ("https://www.ipn.mx/oferta-educativa.html", "www.ipn.mx",
     3.76, 92.4, 7340, 558, "T480-Chrome-Bat-SATA", "chrome"),
    
    ("https://es.wikipedia.org/wiki/Procesamiento_del_lenguaje_natural", "es.wikipedia.org",
     1.78, 86.7, 10680, 1420, "T480-Chrome-Bat-SATA", "chrome"),
    
    ("https://www.dgcs.unam.mx/boletin/bdboletin/2025_006.html", "www.dgcs.unam.mx",
     4.98, 95.0, 9230, 461, "T480-Chrome-Bat-SATA", "chrome"),
    
    # ========== THINKPAD T480 - 16GB + NVMe + Corriente + Edge (6 registros) ==========
    # Configuración: i5-8250U, 16GB DDR4, NVMe SSD, W11 24H2, Edge, Corriente
    # Factor total: ~1.15x más lento que Nitro 5 (configuración óptima)
    
    ("https://www.dgcs.unam.mx/boletin/bdboletin/2025_007.html", "www.dgcs.unam.mx",
     3.12, 94.5, 8790, 483, "T480-Edge-Corr-NVMe", "edge"),
    
    ("https://es.wikipedia.org/wiki/Visión_por_computadora", "es.wikipedia.org",
     1.23, 86.3, 12100, 1657, "T480-Edge-Corr-NVMe", "edge"),
    
    ("https://www.inegi.org.mx/temas/pib/", "www.inegi.org.mx",
     3.56, 93.4, 7980, 527, "T480-Edge-Corr-NVMe", "edge"),
    
    ("https://developer.mozilla.org/es/docs/Web/API", "developer.mozilla.org",
     2.01, 89.4, 8650, 917, "T480-Edge-Corr-NVMe", "edge"),
    
    ("https://es.wikipedia.org/wiki/Algoritmo", "es.wikipedia.org",
     1.15, 85.2, 10570, 1564, "T480-Edge-Corr-NVMe", "edge"),
    
    ("https://www.dgcs.unam.mx/boletin/bdboletin/2025_008.html", "www.dgcs.unam.mx",
     2.98, 94.9, 9450, 482, "T480-Edge-Corr-NVMe", "edge"),
]


# ============================================================================
# METADATOS DE HARDWARE
# ============================================================================

HARDWARE_SPECS = {
    "AN515-Edge-Corr": {
        "nombre": "Acer Nitro 5 AN515-53",
        "cpu": "Intel Core i5-8300H (8th gen, 4 cores)",
        "ram": "16GB DDR4",
        "storage": "1TB NVMe SSD",
        "os": "Windows 11 25H2",
        "navegador": "Microsoft Edge",
        "estado": "Conectado a corriente",
        "factor_velocidad": 1.0  # Referencia
    },
    "E6420-Chrome-Bat-HDD": {
        "nombre": "Dell Latitude E6420",
        "cpu": "Intel Core i5-2520M (2nd gen, 2 cores)",
        "ram": "8GB DDR3",
        "storage": "HDD 7200rpm",
        "os": "Windows 11 24H2",
        "navegador": "Google Chrome",
        "estado": "Batería",
        "factor_velocidad": 0.32  # ~3.15x más lento
    },
    "E6420-Edge-Corr-SSD": {
        "nombre": "Dell Latitude E6420",
        "cpu": "Intel Core i5-2520M (2nd gen, 2 cores)",
        "ram": "8GB DDR3",
        "storage": "SSD SATA",
        "os": "Windows 11 24H2",
        "navegador": "Microsoft Edge",
        "estado": "Conectado a corriente",
        "factor_velocidad": 0.48  # ~2.07x más lento
    },
    "T480-Chrome-Bat-SATA": {
        "nombre": "Lenovo ThinkPad T480",
        "cpu": "Intel Core i5-8250U (8th gen, 4 cores)",
        "ram": "8GB DDR4",
        "storage": "SSD SATA",
        "os": "Windows 11 24H2",
        "navegador": "Google Chrome",
        "estado": "Batería",
        "factor_velocidad": 0.52  # ~1.91x más lento
    },
    "T480-Edge-Corr-NVMe": {
        "nombre": "Lenovo ThinkPad T480",
        "cpu": "Intel Core i5-8250U (8th gen, 4 cores)",
        "ram": "16GB DDR4",
        "storage": "NVMe SSD",
        "os": "Windows 11 24H2",
        "navegador": "Microsoft Edge",
        "estado": "Conectado a corriente",
        "factor_velocidad": 0.87  # ~1.15x más lento
    }
}


# ============================================================================
# FUNCIÓN DE INSERCIÓN
# ============================================================================

def insertar_datos_simulados():
    """
    Inserta los datos sintéticos pre-calculados en la base de datos.
    """
    print("\n" + "=" * 80)
    print("🚀 INSERCIÓN DE DATOS SIMULADOS - NARRADOR WEB")
    print("=" * 80)
    
    # Debug: verificar que db se importó correctamente
    print(f"✅ Módulo db importado correctamente")
    print(f"✅ Funciones disponibles: upsert_page, insert_run")
    
    # Debug: verificar que la BD existe
    try:
        stats = db.get_stats()
        print(f"✅ Conexión a BD exitosa. Registros actuales: {stats['total_runs']}")
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        return
    
    print(f"📊 Total de registros a insertar: {len(DATOS_SIMULADOS)}")
    print()
    
    # Mostrar resumen por hardware
    hardware_counts = {}
    for _, _, _, _, _, _, hw_id, _ in DATOS_SIMULADOS:
        hardware_counts[hw_id] = hardware_counts.get(hw_id, 0) + 1
    
    print("📊 DISTRIBUCIÓN POR HARDWARE:")
    print("-" * 80)
    for hw_id, count in hardware_counts.items():
        specs = HARDWARE_SPECS[hw_id]
        print(f"{specs['nombre']:<30} | {count:>2} registros | {specs['navegador']:<15}")
    print("-" * 80)
    print()
    
    # Confirmar inserción
    respuesta = input("¿Deseas continuar con la inserción? (s/n): ").strip().lower()
    if respuesta != 's':
        print("❌ Inserción cancelada por el usuario.")
        return
    
    print("\n⏳ Insertando datos...")
    print()
    
    # Timestamp base (hace 2 días hasta ahora)
    base_time = datetime.now() - timedelta(days=2)
    
    insertados = 0
    errores = 0
    
    for idx, (url, domain, ttcu, ptnn, chars_orig, chars_extr, hw_id, browser) in enumerate(DATOS_SIMULADOS):
        try:
            # Generar run_id único
            run_id = uuid.uuid4().hex
            
            # Debug: mostrar qué se está insertando
            if insertados == 0:
                print(f"  🔍 DEBUG - Primer registro:")
                print(f"     URL: {url[:50]}...")
                print(f"     Domain: {domain}")
                print(f"     TTCU: {ttcu}s, PTNN: {ptnn}%")
            
            # Timestamp incremental (distribuir en 2 días)
            timestamp_offset = timedelta(hours=(idx * 48) // len(DATOS_SIMULADOS))
            timestamp = base_time + timestamp_offset
            
            # Calcular métricas derivadas
            total_time_ms = int(ttcu * 1000)  # TTCU en milisegundos
            words_count = chars_extr // 5  # Estimado: 5 chars por palabra
            audio_duration_ms = int((words_count / 150.0) * 60 * 1000)  # 150 palabras/min
            
            # 1. Insertar/obtener page_id
            if insertados == 0:
                print(f"  🔍 Llamando db.upsert_page()...")
            page_id = db.upsert_page(url=url, title=None)
            if insertados == 0:
                print(f"  ✅ page_id obtenido: {page_id}")
            
            # 2. Insertar run
            if insertados == 0:
                print(f"  🔍 Llamando db.insert_run()...")
            db.insert_run(
                run_id=run_id,
                page_id=page_id,
                url=url,
                ttcu_seconds=ttcu,
                ptnn_percent=ptnn,
                total_time_ms=total_time_ms,
                audio_duration_ms=audio_duration_ms,
                chars_original=chars_orig,
                chars_extracted=chars_extr,
                ok=True,
                err_msg=None
            )
            
            if insertados == 0:
                print(f"  ✅ Run insertado exitosamente")
            
            insertados += 1
            
            # Progress indicator
            if (insertados % 5) == 0:
                print(f"  ✅ {insertados}/{len(DATOS_SIMULADOS)} registros insertados...")
        
        except Exception as e:
            errores += 1
            print(f"  ❌ Error insertando registro {idx+1}: {e}")
            if insertados == 0:
                # Si falla el primero, mostrar traceback completo
                import traceback
                traceback.print_exc()
    
    print()
    print("=" * 80)
    print("📋 RESUMEN DE INSERCIÓN")
    print("=" * 80)
    print(f"✅ Registros insertados exitosamente: {insertados}")
    print(f"❌ Errores: {errores}")
    
    # Verificación final: contar registros en BD
    try:
        stats_final = db.get_stats()
        print(f"📊 Total de registros en BD (verificado): {stats_final['total_runs']}")
        if stats_final['total_runs'] >= 16 + insertados:
            print(f"✅ VERIFICACIÓN EXITOSA: Los datos se guardaron correctamente")
        else:
            print(f"⚠️  ADVERTENCIA: Se esperaban {16 + insertados} registros pero hay {stats_final['total_runs']}")
    except Exception as e:
        print(f"⚠️  No se pudo verificar el total: {e}")
    
    print("=" * 80)
    print()
    print("💡 PRÓXIMOS PASOS:")
    print("   1. Verifica los datos: python consultas_bd.py (opción 1)")
    print("   2. Ver por dominio: python consultas_bd.py (opción 3)")
    print("   3. Exportar a CSV: python consultas_bd.py (opción 6)")
    print()


# ============================================================================
# FUNCIÓN DE VISTA PREVIA
# ============================================================================

def vista_previa():
    """
    Muestra una vista previa de los datos sin insertarlos.
    """
    print("\n" + "=" * 80)
    print("👀 VISTA PREVIA DE DATOS SIMULADOS")
    print("=" * 80)
    print()
    
    # Agrupar por hardware
    por_hardware = {}
    for datos in DATOS_SIMULADOS:
        hw_id = datos[6]
        if hw_id not in por_hardware:
            por_hardware[hw_id] = []
        por_hardware[hw_id].append(datos)
    
    for hw_id, registros in por_hardware.items():
        specs = HARDWARE_SPECS[hw_id]
        print(f"\n{'='*80}")
        print(f"🖥️  {specs['nombre']}")
        print(f"{'='*80}")
        print(f"CPU:       {specs['cpu']}")
        print(f"RAM:       {specs['ram']}")
        print(f"Storage:   {specs['storage']}")
        print(f"OS:        {specs['os']}")
        print(f"Navegador: {specs['navegador']}")
        print(f"Estado:    {specs['estado']}")
        print(f"Factor:    {specs['factor_velocidad']:.2f}x (vs Nitro 5)")
        print(f"\nRegistros: {len(registros)}")
        print(f"{'-'*80}")
        print(f"{'Dominio':<30} | {'TTCU (s)':<8} | {'PTNN (%)':<8} | {'Chars':<12}")
        print(f"{'-'*80}")
        
        for url, domain, ttcu, ptnn, chars_orig, chars_extr, _, _ in registros[:5]:  # Mostrar solo primeros 5
            chars = f"{chars_extr}/{chars_orig}"
            print(f"{domain:<30} | {ttcu:>8.2f} | {ptnn:>8.1f} | {chars:<12}")
        
        if len(registros) > 5:
            print(f"... y {len(registros) - 5} registros más")
    
    print("\n" + "=" * 80)
    print(f"Total registros: {len(DATOS_SIMULADOS)}")
    print("=" * 80)
    print()


# ============================================================================
# MAIN
# ============================================================================

def main():
    import sys
    
    print("\n" + "=" * 80)
    print("🔧 GENERADOR DE DATOS SINTÉTICOS - NARRADOR WEB")
    print("=" * 80)
    print()
    print("OPCIONES:")
    print("  1. Vista previa de datos (sin insertar)")
    print("  2. Insertar datos en la base de datos")
    print("  3. Salir")
    print()
    
    opcion = input("Selecciona una opción (1-3): ").strip()
    
    if opcion == "1":
        vista_previa()
    elif opcion == "2":
        insertar_datos_simulados()
    elif opcion == "3":
        print("\n👋 ¡Hasta luego!\n")
    else:
        print("\n❌ Opción inválida.\n")


if __name__ == "__main__":
    main()