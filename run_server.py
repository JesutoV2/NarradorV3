import sys
import os
import traceback
import shutil

# 1. Inyectar la ruta ANTES de importar módulos locales
if getattr(sys, 'frozen', False):
    # Ejecutable de PyInstaller
    application_path = sys._MEIPASS
    sys.path.insert(0, application_path)
else:
    # Script normal
    application_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(application_path, "src", "backend"))

try:
    import uvicorn
    from app.main import app as fastapi_app
    import logging
except Exception as e:
    print("❌ Error fatal al importar dependencias internas:")
    traceback.print_exc()
    input("\nPresiona ENTER para salir...")
    sys.exit(1)

# Silenciar logs excesivos de uvicorn para una terminal más limpia
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

def print_ui():
    print("="*60)
    print("🎙️  NARRADOR WEB V2 - MOTOR LOCAL INICIADO")
    print("="*60)
    print("\nEl servidor está corriendo de forma segura en tu equipo.")
    print("Por favor, no cierres esta ventana mientras uses el narrador.\n")
    print("INSTRUCCIONES DE INSTALACIÓN (solo la primera vez):")
    print("1. Abre Microsoft Edge.")
    print("2. Escribe 'edge://extensions/' en la barra de búsqueda.")
    print("3. Activa el 'Modo de desarrollador' (menú izquierdo).")
    print("4. Haz clic en 'Cargar desempaquetada' y selecciona la carpeta 'extension'")
    print("   que apareció junto a este programa.")
    print("\n------------------------------------------------------------")
    print("Presiona Ctrl+C en esta ventana para apagar el motor.")
    print("------------------------------------------------------------\n")

def extract_extension_if_needed():
    if not getattr(sys, 'frozen', False):
        return # No hacer nada si no es un .exe

    try:
        exe_path = os.path.dirname(sys.executable)
        extension_dest_path = os.path.join(exe_path, "extension")
        
        # La ruta fuente dentro del .exe (definida en el comando de PyInstaller)
        extension_source_path = os.path.join(sys._MEIPASS, "extension")

        print("📦 Verificando la carpeta de la extensión...")
        shutil.copytree(extension_source_path, extension_dest_path, dirs_exist_ok=True)
        print("✅ La carpeta 'extension' está lista.\n")
    except Exception as e:
        print(f"⚠️  No se pudo extraer la carpeta de la extensión: {e}")
        print("   Por favor, extrae la carpeta 'extension' manualmente.\n")

if __name__ == "__main__":
    try:
        extract_extension_if_needed()
        print_ui()
        # Pasamos el objeto de la aplicación directamente en lugar del string
        uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="warning")
    except Exception as e:
        print("\nOCURRIO UN ERROR FATAL AL INICIAR EL SERVIDOR:")
        traceback.print_exc()
        input("\nPresiona ENTER para salir...")