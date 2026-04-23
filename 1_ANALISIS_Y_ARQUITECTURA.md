# Analisis y Arquitectura - Narrador V2

## Objetivo Principal

Procesar paginas web (HTML/CSS), filtrar componentes no deseados (anuncios,
menus, pies de pagina) y narrar unicamente el contenido principal usando
sintesis de voz, evaluando al mismo tiempo metricas de rendimiento.

## Metricas de Rendimiento

- TTCU (Tiempo Hasta Contenido Util): Segundos transcurridos desde que se
  solicita la narracion hasta que inicia el audio.
- PTNN (Proporcion de Texto No-Informativo Narrado): Porcentaje de caracteres
  eliminados (basura) respecto al HTML original.

## Flujo de Procesamiento

1. La extension (content.js) captura el HTML integro de la pagina y lo envia via
   POST al endpoint /speak.
2. El orquestador (main.py) recibe la peticion, realiza una auto-limpieza de
   audios residuales previos y transfiere el HTML.
3. El filtro (filters.py) usa BeautifulSoup4 y lxml para eliminar etiquetas
   inutiles y seleccionar el contenedor principal con mayor puntaje de
   relevancia.
4. El extractor (extractor.py) toma el contenedor limpio, aplica limpieza de
   caracteres (normalizer.py) y extrae los parrafos en orden secuencial.
5. El motor TTS (tts.py) utiliza pyttsx3 para convertir el texto extraido en un
   archivo de audio .wav local.
6. Las metricas TTCU y PTNN son calculadas y almacenadas en la base de datos
   (db.py).
7. La extension recibe el ID y delega a offscreen.js la reproduccion silenciosa
   del endpoint /stream.

## Modulos del Backend

- main.py: API REST central. Define endpoints, orquesta el flujo y maneja la
  limpieza de archivos residuales generados.
- filters.py: Logica de limpieza del DOM. Oculta elementos, desenvuelve web
  components y elige heuristicamente contenedores semanticos validos.
- extractor.py: Iterador del DOM limpio que extrae los bloques de texto
  asegurandose que cumplan con las reglas de legibilidad y longitud minima.
- normalizer.py: Set de utilerias de expresiones regulares para particionar o
  normalizar espacios en strings limpios.
- tts.py: Integracion con SAPI5. Selecciona la voz adecuada del sistema
  operativo y renderiza el texto en un archivo de formato wav, con manejo de
  fallas.
- db.py: Gestion nativa de la base de datos SQLite (seminario_narrador.db).
  Evita duplicidades y genera los IDs de cada solicitud (run_id).

## Librerias Clave del Sistema

- FastAPI y Uvicorn: Responsables del ciclo de vida del servidor web y de la API
  expuesta a la extension de Edge.
- BeautifulSoup4 y lxml: Motores de parseo estructural del DOM, veloces y
  tolerantes a errores en etiquetas HTML.
- pyttsx3: Motor Text-to-Speech totalmente offline.
- pydantic: Define las reglas y tipos de datos que la API espera recibir
  (payloads).

## Utilidades y Testing

- insert.py: Inyector de datos de prueba, simula iteraciones de hardware desde
  la CLI.
- consultas_bd.py: Panel interactivo de consola para realizar lecturas,
  promedios grupales y extraccion de metricos a CSV.

---

Nota para la IA: El proyecto requiere estricto orden en el pase de datos entre
modulos para evitar cuellos de botella.
