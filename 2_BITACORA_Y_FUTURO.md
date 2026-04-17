# 🧠 Bitácora de Proyecto y Hoja de Ruta (Contexto IA)

> **Aviso para asistentes de IA:** Este archivo, junto con `1_ANALISIS_Y_ARQUITECTURA.md` y `README.md`, conforman el contexto absoluto de este proyecto. Deben consultarse antes de sugerir cambios grandes. **Estos 3 archivos deben actualizarse constantemente conforme el proyecto evolucione para no perder la memoria de trabajo.**

## 📌 Estado Actual del Proyecto (Noviembre 2025)

1. **Estabilidad Lograda:** El sistema funciona perfectamente en `Python 3.11` usando `FastAPI` y `Uvicorn`. Se eliminó el uso de Python 3.14 que causaba errores de compilación con la librería `spacy`.
2. **Base de Datos Unificada:** Se resolvió un problema de duplicidad de bases de datos. Actualmente **SOLO existe una base de datos activa** ubicada en `src/backend/seminario_narrador.db`. Todo el código (`main.py`, `insert.py`, `consultas_bd.py`) apunta correctamente hacia la carpeta `app/db.py`.
3. **Simulador de Datos:** El script `insert.py` inyecta datos sintéticos de 3 configuraciones de hardware distintas, imitando perfectamente la estructura de las pruebas beta en vivo (calculando TTCU y PTNN).
4. **Control de Versiones:** El proyecto está limpio y respaldado en un repositorio privado en GitHub. El archivo `.gitignore` está correctamente configurado para ignorar `venv/`, `*.db`, y audios `*.wav`.

---

## 🚀 Planes a Futuro y Hoja de Ruta

A partir de este punto, el enfoque del proyecto pasará de la "estabilización" a la "preparación para producción y empaquetado". Debemos evitar redundancias, código muerto y mantener el proyecto extremadamente limpio.

Las próximas tareas a realizar se dividirán en las siguientes 4 fases:

### 1. Limpieza de Archivos y Programa

* **Objetivo:** Determinar qué sirve y qué no.
* **Acciones:** Hacer una auditoría profunda de la carpeta del proyecto. Eliminar scripts huérfanos, versiones previas de código, comentarios obsoletos y consolidar utilidades. Queremos un repositorio esbelto y fácil de leer.

### 2. Licenciamiento (Licencia MIT)

* **Objetivo:** Proteger y abrir el software adecuadamente.
* **Acciones:** Entender cómo funciona la licencia MIT. Determinar cómo aplicarla correctamente en el código fuente, la extensión y los metadatos del proyecto, asegurándonos de que está bien redactada e implementada.

### 3. Revisión de Datos y Base de Datos

* **Objetivo:** Validar la integridad para la tesis.
* **Acciones:** Realizar pruebas de usuario beta reales y cruzarlas con los datos simulados de `insert.py`. Asegurarnos de que las consultas, cálculos de TTCU (Tiempo Hasta Contenido Útil) y PTNN (Proporción de Texto No-Informativo) no tengan sesgos o errores matemáticos en su registro.

### 4. Reestructuración Final: "A Prueba de Tontos" (Plug and Play)

* **Objetivo:** Transformar el proyecto de un script de desarrollo a un producto de consumo fácil de instalar.
* **El Problema Actual:** Pedirle a un usuario normal que instale Python, cree un entorno virtual y ejecute `uvicorn` desde la consola es inviable y propenso a errores.
* **La Solución Propuesta:**
  * Separar claramente responsabilidades: La extensión de Edge será puramente el "ojo" y el "input".
  * El núcleo/motor (backend) debe ser reestructurado, compilado y comprimido en un archivo `.zip`.
  * Se buscará usar herramientas (como PyInstaller o similares) para empaquetar FastAPI y el motor de audio en un solo ejecutable portable.
  * **Meta Final:** El usuario "de a pie" solo debe descargar el ZIP, hacer doble clic en el ejecutable (sin instalar Python), cargar la extensión y usar la herramienta instantáneamente.

---

## ⚠️ Lecciones Aprendidas (Para no repetir errores)

* **Cuidado con las versiones de Python:** `spacy` y compiladores C++ fallan en versiones inestables (ej. 3.14). Mantenerse siempre en versiones LTS (3.11 o 3.12).
* **Rutas absolutas vs relativas:** Al ejecutar scripts auxiliares (como `insert.py`), siempre inyectar el `sys.path` usando `Path(__file__).parent / "src" / "backend"` para evitar que se generen archivos `.db` clonados en directorios equivocados.
* **Terminal interactiva:** Scripts que requieran inputs del usuario (`input()`) arrojan `KeyboardInterrupt` si se ejecutan desde la herramienta de depuración (Debug) de VS Code. Ejecutar siempre en la terminal normal.
