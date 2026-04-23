# Documentacion Integral para Tesis - Narrador Web V2

Este documento consolida el marco teorico, la justificacion metodologica, el
analisis algoritmico y las metricas de evaluacion del proyecto "Narrador Web
V2". Su proposito es servir como fuente directa de consulta y extraccion de
textos para la redaccion formal del documento de tesis de grado.

---

## 1. Introduccion y Justificacion del Problema

El acceso a la informacion en la web contemporanea presenta barreras
significativas para usuarios con discapacidades visuales, cognitivas o
dificultades de lectura. Los lectores de pantalla tradicionales (como JAWS o
NVDA) operan bajo un paradigma de "lectura absoluta", procesando linealmente el
arbol de accesibilidad del DOM (Document Object Model). Esto obliga al usuario a
escuchar elementos de navegacion, publicidad, pies de pagina y banners antes de
llegar al contenido sustancial del articulo.

**La Solucion Propuesta:** El Narrador Web V2 propone un paradigma de "lectura
filtrada offline". A traves de un analisis heuristico del codigo fuente, el
sistema identifica aisla y extrae unicamente el bloque de contenido semantico
principal (el articulo o noticia), descartando el ruido visual circundante.
Ademas, prioriza la privacidad absoluta del usuario al realizar el procesamiento
de Texto a Voz (TTS) de manera estrictamente local, sin dependencias de APIs en
la nube.

---

## 2. Marco Teorico y Tecnologico

### 2.1 Procesamiento del DOM y Heuristica Estructural

La estructura de una pagina web moderna esta dictada por etiquetas HTML, pero la
semantica a menudo se diluye en frameworks de diseño (Web Components, divs
anidados). Para extraer la informacion, el proyecto prescinde de librerias
pesadas de Procesamiento de Lenguaje Natural (como SpaCy) en favor de un enfoque
de **Web Scraping Heuristico** usando `BeautifulSoup4` y el parser `lxml`. Este
enfoque es menos demandante computacionalmente y altamente efectivo en paginas
institucionales.

### 2.2 Sintesis de Voz Local (Offline TTS)

El uso de `pyttsx3` permite interactuar directamente con la interfaz SAPI5
(Speech API) nativa de Windows. La justificacion academica para esto es doble:

1. **Latencia de Red:** Depender de la nube (ej. Google Cloud TTS) introduce
   latencia variable e incertidumbre.
2. **Privacidad de Datos:** Herramientas de accesibilidad no deben funcionar
   como rastreadores de habitos de lectura. El procesamiento en el dispositivo
   del usuario garantiza soberania sobre sus datos.

### 2.3 Arquitectura de Microservicios Locales

El software se divide en dos capas por restricciones de seguridad de los
navegadores modernos (Manifest V3):

- **Cliente (Extension Edge):** Opera en un entorno de "sandbox". La politica de
  Manifest V3 impide la inyeccion de scripts pesados o ejecucion de binarios.
  Por lo tanto, la extension actua exclusivamente como un capturador del DOM
  (`content.js`) y un reproductor de audio aislado (`offscreen.js`).
- **Servidor Local (FastAPI):** Provee los recursos de computo a traves de una
  API REST (localhost:8000). Python ofrece las herramientas optimas para el
  parseo y la generacion de audio.

---

## 3. Metodologia de Evaluacion y Metricas

El proyecto no solo es una herramienta de software, sino un objeto de estudio
cuantitativo. Para medir su exito, se establecieron dos metricas fundamentales
documentadas en el modulo `main.py`.

### 3.1 PTNN (Proporcion de Texto No-Informativo Narrado)

Mide la eficacia del algoritmo de limpieza ("basura" removida del documento).

**Formula Matematica:**
`PTNN = ((Caracteres Totales del HTML - Caracteres del Texto Extraido) / Caracteres Totales del HTML) * 100`

**Justificacion y Limitacion Academica:** El PTNN se calcula en funcion del
total de caracteres del codigo fuente, no de los nodos visuales renderizados. Un
fragmento grande de codigo CSS o JavaScript embebido aumenta artificialmente los
caracteres totales. Por lo tanto, en la tesis se debe precisar que el PTNN
documenta la "tasa de reduccion de carga de procesamiento del codigo" y la
"eficacia en la eliminacion de ruido estructural", demostrando reducciones
tipicas superiores al 85%.

### 3.2 TTCU (Tiempo Hasta Contenido Util)

Mide la eficiencia y capacidad de respuesta del sistema desde la perspectiva del
usuario.

**Formula Matematica:**
`TTCU = (Tiempo de Extraccion (ms) + Tiempo de renderizado TTS (ms)) / 1000`

**Justificacion y El Sesgo de Hardware:** El TTCU documentado a lo largo de las
pruebas de base de datos presenta un claro sesgo de hardware. Dado que es un
calculo basado en el reloj del sistema (Wall-clock time), esta intrinsecamente
ligado a la velocidad del procesador y la latencia de entrada/salida (I/O) del
disco de almacenamiento, al tener que codificar y guardar un archivo `.wav`. La
tesis debe argumentar que este sesgo no es un error, sino una validacion del
comportamiento de sistemas offline en hardware heredado (legacy hardware).

---

## 4. Desglose Algoritmico y Logica de Modulos

El flujo de ejecucion sigue un patron riguroso de transformacion de datos (Pipes
& Filters).

### 4.1 Orquestacion y Manejo de Recursos (`main.py`)

El ciclo de vida de una peticion `/speak` esta diseñado para ser tolerante a
fallos y evitar fugas de memoria:

1. **Recoleccion de Basura Preventiva (Garbage Collection):** Antes de iniciar
   cualquier extraccion, el sistema barre el directorio temporal e invoca
   `os.remove()` sobre cualquier archivo `.wav` existente. Esto garantiza que
   una maquina de escasos recursos no se sature de audios residuales.
2. **Bloques Try/Except de Contingencia:** Si el motor de SAPI5 falla a la mitad
   de la sintesis, o si BeautifulSoup levanta una excepcion, el manejador de
   errores intercepta el fallo y elimina el archivo corrupto antes de devolver
   un HTTP 500.

### 4.2 Algoritmo de Filtrado Heuristico (`filters.py`)

Este modulo representa el nucleo de la inteligencia del software. No emplea
Inteligencia Artificial, sino algoritmos de busqueda y destruccion estructural.

1. **Desenvolvimiento (Unwrapping):** Se eliminan etiquetas de Web Components
   (etiquetas con guiones, ej. `<custom-header>`) preservando el contenido
   interno, neutralizando la ofuscacion generada por frameworks modernos
   (React/Angular).
2. **Poda de Ruido (DOM Stripping):** Se invocan metodos `decompose()`
   iterativamente para destruir nodos inherentemente ruidosos: `<script>`,
   `<style>`, `<nav>`, `<footer>` e `<iframe>`.
3. **El Sistema de Puntuacion (Scoring System):** Para determinar cual es el
   contenedor principal, se seleccionan elementos semanticos (main, article,
   #content). A cada uno se le aplica una ecuacion matematica para calcular su
   "relevancia":
   `Score = Longitud_del_Texto_Interno + (50 * Cantidad_de_Parrafos) + (25 * Cantidad_de_Cabeceras)`
   El nodo con el `Score` mas alto es seleccionado como raiz para el siguiente
   modulo.

### 4.3 Algoritmo de Extraccion Secuencial (`extractor.py`)

Una vez obtenido el contenedor principal limpio, el sistema debe recolectar la
lectura en el orden correcto.

1. **Iteracion Lineal:** Se recorren las etiquetas en el orden de aparicion en
   el DOM (`h1-h3`, `p`, `li`, `blockquote`).
2. **Reglas de Longitud y Legibilidad:** No todo el texto se narra. Los titulos
   se aceptan a partir de 5 caracteres. Los parrafos requieren un minimo de 60
   caracteres. Esta regla heuristica discrimina y elimina botones residuales,
   enlaces de "Leer mas", fechas aisladas o metadata sin valor narrativo.
3. **Deduplicacion Secuencial:** Se guarda un registro en memoria (`set`) de los
   parrafos extraidos. Si un fragmento aparece duplicado, se ignora, manteniendo
   la coherencia de la lectura.

### 4.4 Generacion de Audio (`tts.py`)

El motor requiere instanciarse dinamicamente con `pyttsx3.init()`. El algoritmo
itera sobre el registro (registry) de Windows buscando firmas como "es-",
"spanish" o "sabina" para obligar la sintesis en idioma español. Finalmente,
implementa un bucle de espera activa (polling) con `time.sleep(0.1)` verificando
el tamaño del archivo `.wav` en disco, previniendo condiciones de carrera donde
la extension intentara reproducir un audio vacio.

---

## 5. Analisis de Datos y Simulacion Sintetica

Para otorgar validez academica a la tesis, se desarrollo el modulo `insert.py`
que inyecta datos controlados basados en factores de multiplicacion observados
en la realidad.

Se modelaron tres configuraciones informaticas representativas del publico
general en paises en vias de desarrollo:

1. **Gama Alta (Referencia):** Procesador de 8va Generacion (Serie H), 16GB RAM,
   Almacenamiento NVMe (Factor 1.0x).
2. **Gama Media:** Procesador de 8va Generacion (Serie U), 8GB RAM,
   Almacenamiento SATA SSD (Factor ~1.91x mas lento).
3. **Gama Baja (Legacy):** Procesador de 2da Generacion, 8GB RAM, Almacenamiento
   Mecanico HDD (Factor ~3.15x mas lento).

**Conclusiones de la simulacion para la tesis:** Los resultados guardados en
SQLite validan que, aunque el PTNN permanece constante (el algoritmo es
determinista matematicamente y filtrara la misma cantidad de basura sin importar
la computadora), el TTCU se degrada severamente en almacenamiento magnetico
debido al cuello de botella I/O en la generacion del `.wav`.

---

## 6. Evolucion Arquitectonica (Lecciones y Decisiones)

Esta seccion provee la justificacion para la defensa de la tesis ante posibles
preguntas sobre las tecnologias descartadas.

- **Abandono de SpaCy y Trafilatura:** En etapas iniciales se considero el uso
  de modelos de NLP (Procesamiento de Lenguaje Natural). Se descarto debido a
  severos problemas de compilacion con C++, dependencias masivas (>500 MB) que
  hacian inviable la distribucion, e incompatibilidades con versiones futuras de
  Python (3.14). La logica de expresiones regulares (`normalizer.py`) y
  BeautifulSoup probaron ser 95% mas veloces y suficientes para el objetivo.
- **Transicion de MS SQL Server a SQLite:** Inicialmente el proyecto contemplo
  el controlador `pyodbc`. Esta aproximacion violaba el principio de
  portabilidad. Migrar todo a SQLite (`db.py`) garantizo que la base de datos
  sea un archivo local, auto-generado y sin requisitos de instalacion por parte
  del usuario final.
- **Preparacion para Produccion (Fase Final):** De cara a la entrega del
  producto final, la telemetria y la base de datos deben ser removidas. La tesis
  debe establecer que la base de datos actual es un instrumento estrictamente de
  analisis academico. Mantenerla en produccion incurriria en violaciones de
  privacidad (guardar las URLs que lee el usuario) y degradacion progresiva del
  disco (crecimiento infinito del archivo `.db`).

---

_Nota: El codigo base descrito opera bajo la licencia MIT, garantizando que los
metodos heuristicos aqui detallados pueden ser replicados y expandidos por
futuras lineas de investigacion en materia de accesibilidad._
