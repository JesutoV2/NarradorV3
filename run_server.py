import sys
import os
import uvicorn
import logging

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
    # Inyectar la ruta correcta para que las importaciones relativas funcionen
    if getattr(sys, 'frozen', False):
        # Ejecutable de PyInstaller
        application_path = sys._MEIPASS
    else:
        # Script normal
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    sys.path.insert(0, os.path.join(application_path, "src", "backend"))
    
    print_ui()
    
    # Iniciar FastAPI programáticamente
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="warning")