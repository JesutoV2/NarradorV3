# Bitacora de Proyecto y Hoja de Ruta

Aviso para asistentes de IA: Este archivo, junto con
1_ANALISIS_Y_ARQUITECTURA.md y README.md, conforman el contexto absoluto y la
memoria a largo plazo de este proyecto. Deben consultarse antes de sugerir
cambios en la base de codigo y actualizarse constantemente.

## Contexto y Estado del Proyecto (Noviembre 2025)

El Narrador Web V2 es una herramienta de accesibilidad enfocada en extraer y
leer el contenido principal de paginas web de forma privada y local. El backend
opera sobre Python 3.11 usando FastAPI, mientras que el frontend es una
extension adaptada a Manifest V3 de Edge.

El proyecto logro consolidarse y estabilizarse, eliminando duplicidad de bases
de datos, apuntando unicamente al motor SQLite nativo alojado en
`src/backend/seminario_narrador.db`.

## Registro de Cambios y Trabajo Realizado

Se ha trabajado en depurar exhaustivamente el backend en las Fases 1 y 2 de
preparacion para produccion:

- Fase 1 (Limpieza de Archivos y Dependencias):
  - Auditoria completada. Se eliminaron modulos y utilidades huerfanas como
    `segmenter.py`, `db_sqlite.py` y scripts `.sql`.
  - Se removio logica o metodos alias en `extractor.py` y `filters.py`.
  - Se refactorizo el requirements.txt; se eliminaron librerias pesadas como
    `spacy`, `trafilatura` y conectores como `pyodbc`. Se agrego formalmente
    `lxml`.
  - Se integro un esquema de prevencion de fugas en disco: `main.py` y `tts.py`
    ahora barren y eliminan los archivos `.wav` temporales antes de cada
    peticion, o en medio de una falla del motor SAPI5, asegurando que el
    directorio de audios se mantenga en cero acumulos.

- Fase 2 (Licenciamiento):
  - Se aprobo y configuro la Licencia MIT. Se genero el archivo pertinente y fue
    atado en la documentacion oficial (README) y el copyright del autor,
    brindando proteccion legal ante un despliegue de produccion.

- Fase 4 (Empaquetado Plug and Play):
  - Se completo exitosamente la compilacion del backend en un archivo
    `NarradorMotor.exe` portable usando PyInstaller.
  - Se creo el script `run_server.py` como punto de entrada, el cual inicia
    Uvicorn programaticamente y provee una interfaz de usuario en la terminal.
  - Se implemento un sistema de deteccion de rutas dinamicas (`sys.executable` y
    `sys._MEIPASS`) en `main.py` y `db.py` para asegurar que la base de datos y
    los audios se guarden de forma relativa al ejecutable, garantizando su
    portabilidad.
  - Se resolvieron errores de importacion en el entorno compilado al pasar el
    objeto de la aplicacion FastAPI directamente a Uvicorn, en lugar de un
    string.

## Hoja de Ruta Activa

Con la estabilidad del sistema terminada, las siguientes fases migran hacia
empaquetado y documentacion.

### Fase 3: Revision de Datos

- Objetivo: Validar la integridad logica de las pruebas de cara a la tesis de
  grado.
- Acciones a seguir: Confirmar la validez de los resultados sinteticos de
  `insert.py` contra capturas de pruebas beta en vivo. Revisar a detalle que los
  calculos matematicos en la extraccion de chars originales (PTNN) y toma de
  tiempos MS (TTCU) no cuenten con un margen de sesgo por hardware.

### Fase 4: Reestructuracion Final (Plug and Play)

- Objetivo: Transformar el proyecto de un script dependiente de CLI a un
  producto consumible por el publico final con accesibilidad web.
- Problema central: Ejecutar entornos virtuales de Python es propenso a fallas
  en usuarios estandar.
- Solucion: Compilar el entorno entero en un ejecutable cerrado empleando
  herramientas como PyInstaller.
- Meta: El usuario debe descargar un .zip, arrastrar la extension al navegador,
  y prender un ejecutable `.exe` sin requerir instalaciones pesadas del
  lenguaje.

## Lecciones Aprendidas (Para no repetir)

1. Rutas del Sistema: Al ejecutar scripts desde ubicaciones diferentes, la
   libreria sqlite nativa creara archivos .db huerfanos. Siempre se debe
   inyectar de manera absoluta al PYTHONPATH el directorio backend.
2. Higiene del Disco: Los procesos temporales que involucren I/O (lectura y
   escritura de audios) deben obligatoriamente vaciar la basura al instanciar
   nuevas solicitudes para evitar sobrecarga en la maquina cliente.
3. Modulos Ligeros: Es indispensable verificar el arbol de requerimientos en
   desarrollo para evitar compilar ejecutables inflados por dependencias
   analiticas no utilizadas.
