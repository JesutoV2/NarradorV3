# 🎙️ Narrador Web V2

Herramienta de accesibilidad web diseñada para extraer, limpiar y narrar contenido principal de páginas web, descartando "ruido" (anuncios, menús) y evaluando el rendimiento a través de métricas específicas (TTCU y PTNN).

## ⚙️ ¿Cómo funciona?

El sistema se divide en dos partes:

1. **La Extensión (Frontend):** Se instala en Microsoft Edge. Actúa como los "ojos" del usuario, capturando el código de la página web actual y enviándolo al motor.
2. **El Motor (Backend):** Un servidor local construido en Python (FastAPI) que recibe la página, la limpia usando filtros inteligentes (`BeautifulSoup`), extrae el texto útil, lo convierte en audio (`pyttsx3`) y lo devuelve a la extensión para su reproducción. Además, registra métricas de rendimiento en una base de datos SQLite.

---

## 🚀 Guía de Instalación y Uso (Desarrollo)

**Requisitos:** Windows 11 y Python 3.11 instalado.

### 1. Preparar el Entorno Virtual

Abre una terminal en la raíz del proyecto y ejecuta:

```powershell
python -m venv .venv
.venv\\Scripts\\activate
```

### 2. Instalar Dependencias

```powershell
pip install -r requirements.txt
```

### 3. Arrancar el Servidor (Motor Backend)

Para que el sistema funcione, el motor debe estar encendido.

```powershell
cd src\backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

*Nota: El servidor estará escuchando en el puerto 8000. Si está ocupado, usa el 8010 y actualiza `extension/content.js`.*

### 4. Cargar la Extensión en Microsoft Edge

1. Abre Microsoft Edge y ve a `edge://extensions/`.
2. Activa el **"Modo de desarrollador"** (menú izquierdo).
3. Haz clic en **"Cargar desempaquetada"** y selecciona la carpeta `extension/` de este proyecto.

### 5. Modo de Uso

1. Navega a una página web con artículos o noticias (ej. Wikipedia, INEGI, SciELO).
2. Haz clic en el botón flotante **"Narrar"**.
3. El sistema procesará el texto (calculando el TTCU y PTNN) y comenzará la reproducción de audio en menos de 12 segundos. Todo el proceso es **100% offline y privado**.

---

## 📊 Scripts Auxiliares y Datos

En la raíz del proyecto encontrarás herramientas para analizar el rendimiento del sistema:

* **`insert.py`**: Generador de datos sintéticos. Simula cómo rendiría el programa en 3 computadoras con hardware diferente (Gama Baja, Media y Alta) basándose en registros reales. (Ejecutar solo 1 vez).
* **`consultas_bd.py`**: Herramienta interactiva en terminal para visualizar la base de datos (`seminario_narrador.db`), ver promedios, buscar por dominios y exportar los datos a CSV para análisis en Excel.

---
*Nota para IAs y Asistentes: Para entender el panorama completo del código y los planes futuros, consultar obligatoriamente los archivos `1_ANALISIS_Y_ARQUITECTURA.md` y `2_BITACORA_Y_FUTURO.md`.*
