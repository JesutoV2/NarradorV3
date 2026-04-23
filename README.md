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

## Scripts de Analisis

- insert.py: Inyecta datos sinteticos de pruebas de hardware (ejecutar una vez).
- consultas_bd.py: Interfaz CLI para ver estadisticas, exportar a CSV y analizar
  metricas.

## Licencia

Este proyecto esta bajo la Licencia MIT. Consulta el archivo LICENSE.

---

Notas: Para entender el panorama completo, consultar obligatoriamente
1_ANALISIS_Y_ARQUITECTURA.md y 2_BITACORA_Y_FUTURO.md.
