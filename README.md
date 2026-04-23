# Narrador Web V2

Herramienta de accesibilidad web disenada para extraer, limpiar y narrar el
contenido principal de paginas web, descartando el ruido visual (anuncios,
menus) y evaluando el rendimiento a traves de metricas especificas (TTCU y
PTNN).

## Funcionamiento

1. Frontend (Extension): Se instala en Microsoft Edge. Captura el codigo de la
   pagina web actual y lo envia al motor.
2. Backend (Motor): Servidor local en Python (FastAPI). Recibe el HTML, lo
   limpia con BeautifulSoup, extrae el texto, lo convierte en audio con pyttsx3,
   lo devuelve a la extension y registra las metricas en SQLite.

## Instalacion y Uso (Desarrollo)

Requisitos: Windows 11, Python 3.11.

1. Preparar entorno e instalar dependencias: python -m venv .venv
   .venv\Scripts\activate pip install -r requeriments.txt

2. Arrancar el servidor: cd src\backend uvicorn app.main:app --host 127.0.0.1
   --port 8000 --reload

3. Instalar la extension: Abre Edge, ve a edge://extensions/, activa "Modo de
   desarrollador", clic en "Cargar desempaquetada" y selecciona la carpeta
   `extension/`.

4. Uso: Navega a un articulo, haz clic en el boton "Narrar" de la extension. El
   proceso operara 100% offline.

## Instalacion y Uso (Version Portable)

Esta versión está diseñada para usuarios finales sin conocimientos técnicos,
empaquetada en un solo archivo.

1. **Ejecutar `NarradorMotor.exe`**. Al iniciarse, el programa creará
   automáticamente una carpeta llamada `extension` a su lado.
2. **Instalar la extensión en Edge**: a. Abre Microsoft Edge y ve a la dirección
   `edge://extensions/`. b. Activa el **"Modo de desarrollador"** en el menú de
   la izquierda. c. Haz clic en **"Cargar desempaquetada"** y selecciona la
   carpeta `extension` que se acaba de crear.
3. Una vez instalada, el botón "Narrar" aparecerá en las páginas web para su
   uso. El servidor en la terminal debe permanecer abierto.

## Scripts de Analisis

- insert.py: Inyecta datos sinteticos de pruebas de hardware (ejecutar una vez).
- consultas_bd.py: Interfaz CLI para ver estadisticas, exportar a CSV y analizar
  metricas.

## Licencia

Este proyecto esta bajo la Licencia MIT. Consulta el archivo LICENSE.

---

Nota para IAs: Para entender el panorama completo, consultar obligatoriamente
1_ANALISIS_Y_ARQUITECTURA.md y 2_BITACORA_Y_FUTURO.md.
