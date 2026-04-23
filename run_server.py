import sys
import os
import traceback

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
    print("INSTRUCCIONES PARA EL NAVEGADOR:")
    print("1. Abre Microsoft Edge.")
    print("2. Escribe 'edge://extensions/' en la barra de búsqueda.")
    print("3. Activa el 'Modo de desarrollador' (menú izquierdo).")
    print("4. Haz clic en 'Cargar desempaquetada' y selecciona la carpeta 'extension'.")
    print("\n------------------------------------------------------------")
    print("Presiona Ctrl+C en esta ventana para apagar el motor.")
    print("------------------------------------------------------------\n")

if __name__ == "__main__":
    try:
        print_ui()
        # Pasamos el objeto de la aplicación directamente en lugar del string
        uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="warning")
    except Exception as e:
        print("\nOCURRIO UN ERROR FATAL AL INICIAR EL SERVIDOR:")
        traceback.print_exc()
        input("\nPresiona ENTER para salir...")