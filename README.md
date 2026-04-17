
# Ejecución local (Windows 11, Python 3.11)

## 1) Crear y activar entorno

python -m venv .venv
.venv\\Scripts\\activate

## 2) Instalar dependencias

pip install -r requirements.txt

## 3) Arrancar backend (puerto 8000)

cd src\backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

- Si el puerto 8000 está ocupado, usar 8010 y **actualizar la URL** en `extension/content.js`.

## 4) Verificar voces disponibles (opcional)

GET `http://127.0.0.1:8000/voices`

- Debe listar voces SAPI; si no aparece Sabina, el backend **usará una voz en español** como fallback.

## 5) Cargar extensión en Edge

- edge://extensions → "Cargar desempaquetada" → `extension/`

## 6) Probar

- Abrir una página del dataset (UNAM/IPN/INEGI/SciELO/MDN o Wikipedia Portada).
- Clic en **Narrar**.
  - Si en ≤12 s arranca el audio → OK.
  - Si no, el botón pasa a **Error**. Clic otra vez → reinicia.

## Notas

- Si el texto sale muy corto: en `extractor.py` cambiar `favor_precision=True` a `False` y reintentar.
- Si no se oye: comprobar que hay **alguna** voz en español. El endpoint `/voices` ayuda a verificar.
- Todo es **offline**: no se envían datos a la nube.
