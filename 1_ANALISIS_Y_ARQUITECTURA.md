# 🏗️ Arquitectura y Estado del Proyecto - Narrador V2

## 🎯 Objetivo Principal

Procesar páginas web (HTML/CSS), filtrar el "ruido" (anuncios, menús, pies de página) y narrar únicamente el contenido principal y relevante usando síntesis de voz, evaluando métricas de rendimiento (TTCU, PTNN).

## 🧩 Flujo de Datos Actual

1. **Usuario** hace clic en "Narrar" en la página web (`content.js`).
2. La extensión envía el `document.documentElement.outerHTML` íntegro al endpoint `/speak`.
3. **FastAPI (`main.py`)** recibe el HTML.
4. `filters.py` entra en acción:
   - Elimina scripts, estilos, iframes, footers y asides.
   - Busca el contenedor con mayor puntaje (más texto y subtítulos).
5. `extractor.py` toma ese contenedor y filtra párrafos con longitud menor a 60 caracteres (eliminando links cortos o UI suelta).
6. `tts.py` convierte el texto filtrado a `.wav` usando `pyttsx3`.
7. Se insertan las métricas en SQLite.
8. La extensión recibe el `run_id` y delega a `offscreen.js` la reproducción del endpoint `/stream/{run_id}`.

## 📂 Mapa de Módulos (Backend)

| Archivo | Propósito | Estado |
| --------- | ----------- | -------- |
| `main.py` | API REST / Orquestador | 🟢 Funcional |
| `filters.py` | Limpieza de HTML (BeautifulSoup) | 🟢 Funcional / Mejorable |
| `extractor.py` | Recolección de párrafos limpios | 🟢 Funcional |
| `tts.py` | Motor SAPI5 a WAV (`pyttsx3`) | 🟢 Funcional |
| `db_sqlite.py` / `db.py` | Lógica de Base de Datos SQLite | 🟡 Duplicidad detectada |
| `segmenter.py` / `normalizer.py` | Limpieza y chunking de texto | 🟢 Funcional |

## 💻 Mapa de Módulos (Extensión MV3)

| Archivo        | Propósito                                                | Estado       |
|----------------|----------------------------------------------------------|--------------|
| `content.js`   | Botón UI inyectado, máquina de estados y captura de HTML | 🟢 Funcional |
| `offscreen.js` | Reproductor de audio invisible (By-pass límites MV3)     | 🟢 Funcional |

## ⚙️ Métricas Principales

- **TTCU (Tiempo Hasta Contenido Útil):** Segundos desde que se solicita hasta que inicia el audio.
- **PTNN (Proporción de Texto No-Informativo):** % de "basura" (caracteres) removidos del HTML original.

---
*Nota para el Asistente AI: Consultar este archivo para entender el contexto global antes de proponer cambios arquitectónicos severos.*
