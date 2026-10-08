# BBB-Scribe

> **Suite integral para descargar, recomponer y transcribir clases grabadas de BigBlueButton (BBB) a video, audio y apuntes en Markdown con marcas de tiempo.**

---

## Índice

- [Características Principales](#características-principales)
- [Requisitos del Sistema](#requisitos-del-sistema)
- [Instalación Rápida (Paso a Paso)](#instalación-rápida-paso-a-paso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Modo de Uso](#modo-de-uso)
  - [1. Descarga de Clases](#1-descarga-de-clases)
  - [2. Transcripción Automática a Texto / Markdown](#2-transcripción-automática-a-texto--markdown)
- [Modelos de Transcripción (Whisper)](#modelos-de-transcripción-whisper)
- [Integración con Asistentes de IA (Apuntes Técnicos)](#integración-con-asistentes-de-ia-apuntes-técnicos)
- [Decisión de Diseño: Descarte de LLMs Locales (llama.cpp)](#decisión-de-diseño-descarte-de-llms-locales-llamacpp)
- [Solución de Problemas Frecuentes](#solución-de-problemas-frecuentes)

---

## Características Principales

* **Recomposición Fiel de Sesiones:** Une audio, diapositivas vectoriales, trazos de pizarra, movimiento de puntero láser y webcam sincronizada mediante un navegador Chromium headless (*Playwright*).
* **Descarga Directa Ultra Rápida:** Si la clase consistió en compartir pantalla y voz de forma continua, permite extraer y unir los flujos al instante sin renderizado cuadro por cuadro.
* **Transcripción Neuronal Offline (`faster-whisper`):** Convierte el audio de las clases en texto con filtro de silencios (VAD), 100% privado y sin requerir conexión ni claves de API externas.
* **Formato Dual para Estudio:** Exporta automáticamente transcripciones en texto cronológico (`.txt`) y Markdown estructurado (`.md`) con enlaces de tiempo `[HH:MM:SS]` listos para generar apuntes o alimentar modelos de lenguaje.
* **Cero Fricción en Windows:** Incluye accesos directos por lotes (`download.bat` y `transcribe.bat`) y detección automática del entorno virtual local.
* **Gestión Inteligente de FFmpeg:** Detecta binarios locales en `bin/`, en el PATH del sistema o los descarga automáticamente en el primer uso.

---

## Requisitos del Sistema

Antes de comenzar, asegúrate de contar con:

1. **Sistema Operativo:** Windows 10/11, Linux o macOS.
2. **Python:** Versión **3.10** o superior (recomendado 3.10 a 3.12).
   * *Verificar en terminal con:* `python --version`
3. **Espacio en Disco:** Mínimo 3 a 5 GB libres para el entorno virtual, navegador Chromium, modelos Whisper y archivos temporales de video.
4. **Hardware:**
   * **CPU:** Procesador multi-núcleo (Whisper opera por defecto optimizado con cuantización `int8` en CPU).
   * **RAM:** Mínimo 8 GB de memoria RAM (recomendado 16 GB si transcribes con modelos `medium`).
   * **GPU (Opcional):** Tarjeta gráfica NVIDIA con soporte CUDA si deseas acelerar Whisper.

---

## Instalación Rápida (Paso a Paso)

Si vas a clonar el repositorio o compartir la carpeta con compañeros de estudio, sigue estos pasos una única vez:

### 1. Clonar o descomprimir el proyecto
Abre una terminal en la carpeta del proyecto:
```powershell
cd BBB-downloader
```

### 2. Crear el entorno virtual de Python
```powershell
python -m venv .venv
```

### 3. Activar el entorno virtual
* **En Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
  *(Si PowerShell bloquea la ejecución de scripts, ejecuta primero: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*
* **En Windows (CMD / Símbolo del Sistema):**
  ```cmd
  .\.venv\Scripts\activate.bat
  ```
* **En Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```

### 4. Instalar las dependencias de Python
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Instalar el navegador Chromium (Playwright)
> **Muy importante:** Playwright necesita su propio navegador para renderizar las pizarras y diapositivas de BigBlueButton.
```powershell
playwright install chromium
```

### 6. Binarios de FFmpeg
El proyecto comprueba si existen ejecutables en la carpeta `bin/` o en el PATH del sistema. Si no los encuentra, los descargará automáticamente mediante `ffmpeg-downloader` al ejecutar la primera descarga o extracción de audio.

---

## Estructura del Proyecto

```text
BBB-Scribe/
├── .agents/                  # Reglas y directivas de asistencia para IA
├── bin/                      # Binarios de FFmpeg / FFprobe (excluidos de Git)
├── core/
│   ├── direct_extractor.py   # Extracción directa de flujos multimedia crudos
│   ├── downloader.py         # Orquestador del motor de recomposición bbb-dl
│   ├── ffmpeg_locator.py     # Localizador y auto-instalador de FFmpeg
│   ├── transcriber.py        # Motor de transcripción faster-whisper con timestamps
│   └── url_parser.py         # Análisis e inspección de metadatos de enlaces BBB
├── output/                   # Carpeta de salida para videos, audios y transcripciones
├── cli.py                    # Interfaz unificada de comandos
├── download.py               # Lanzador con auto-delegación a .venv para descargas
├── download.bat              # Acceso directo de descarga para Windows (doble clic)
├── transcribe.py             # Lanzador con auto-delegación para transcripciones
├── transcribe.bat            # Acceso directo de transcripción para Windows (doble clic)
├── extract_frame.py          # Extractor quirúrgico de fotogramas por timestamp
├── requirements.txt          # Dependencias del proyecto
├── .gitignore                # Reglas de exclusión de archivos pesados y temporales
└── README.md                 # Documentación técnica del proyecto
```

---

## Modo de Uso

### 1. Descarga de Clases

#### Opción A: Menú Interactivo (Recomendada)
Haz doble clic en `download.bat` o ejecuta:
```powershell
python download.py
```
Pega el enlace de la grabación de BigBlueButton (ejemplo: `https://servidor.edu.ar/playback/presentation/2.3/playback.html?meetingId=...`). El programa analizará la sesión y te presentará 4 modalidades:

1. **Descarga Completa:** Genera un MP4 de alta fidelidad sincronizando pizarra, diapositivas y cámara web.
2. **Descarga Ligera:** Genera el MP4 completo pero omitiendo la cámara del docente (renderiza mucho más rápido).
3. **Descarga Directa:** Extrae y concatena los streams de pantalla compartida y audio al instante.
4. **Solo Audio:** Extrae el audio de la clase en formato MP3 (ideal para ahorrar espacio y transcribir directamente).

#### Opción B: Línea de Comandos (CLI)
```powershell
# Descarga normal completa
python download.py "URL_DE_LA_CLASE"

# Descargar omitiendo la cámara web
python download.py "URL_DE_LA_CLASE" --skip-webcam

# Extraer únicamente el audio en MP3
python download.py "URL_DE_LA_CLASE" --audio-only

# Descarga directa rápida de streams con nombre personalizado
python download.py "URL_DE_LA_CLASE" --direct -f "output/Clase_01.mp4"
```

---

### 2. Transcripción Automática a Texto / Markdown

Una vez descargado el video (`.mp4`) o audio (`.mp3`), puedes convertirlo en texto con marcas de tiempo precisas.

#### Opción A: Modo Interactivo
Haz doble clic en `transcribe.bat` o ejecuta:
```powershell
python transcribe.py
```
El transcriptor listará todos los videos y audios disponibles en la carpeta `output/` y te permitirá elegir cuál procesar indicando su número.

#### Opción B: Modo Directo
```powershell
# Transcribir un archivo específico (modelo 'small' por defecto)
python transcribe.py "output/Clase 1.mp4"

# Utilizar un modelo con mayor precisión semántica
python transcribe.py "output/Clase 1.mp4" --model medium
```

#### Archivos Resultantes en `output/`:
* `output/<nombre>_transcripcion.txt`: Registro cronológico en texto plano (`[00:15:20 - 00:15:45] Texto hablado`).
* `output/<nombre>_transcripcion.md`: Formato Markdown con encabezados estructurados y marcas en negrita (`**[00:15:20]** Texto hablado`), ideal para importar en editores como Obsidian, Notion o VS Code.

---

## Modelos de Transcripción (Whisper)

Puedes elegir el modelo pasando el argumento `--model <nombre>`:

| Modelo | Tamaño Aprox. | Velocidad | Precisión | Caso de Uso Recomendado |
| :--- | :---: | :---: | :---: | :--- |
| **`tiny`** | ~75 MB | Muy rápida | Básica | Pruebas rápidas o equipos con recursos muy limitados. |
| **`base`** | ~145 MB | Rápida | Aceptable | Clases teóricas con audio claro y sin términos complejos. |
| **`small`** *(Por defecto)* | ~480 MB | Equilibrada | Muy buena | **Recomendado para uso general:** Excelente balance entre velocidad en CPU y precisión en español. |
| **`medium`** | ~1.5 GB | Moderada | Sobresaliente | **Recomendado para programación y ciencias exactas:** Reconoce con exactitud palabras técnicas en inglés, sintaxis y nombres de librerías. |

> *Nota:* La primera vez que uses un modelo, se descargará automáticamente y quedará en caché local para futuros usos sin conexión.

---

## Integración con Asistentes de IA (Apuntes Técnicos)

El repositorio cuenta con directivas configuradas en [`.agents/rules/programming-transcriptions-guardrails.md`](.agents/rules/programming-transcriptions-guardrails.md) para asistir en la transformación de transcripciones a apuntes de estudio:

> [!TIP]
> **Sugerencia fundamental de flujo: Prefiere descargar en video (`.mp4`) en lugar de solo audio (`.mp3`)**  
> Si bien la opción de solo audio (`.mp3`) ahorra espacio en disco, contar con el archivo `.mp4` en `output/` permite que la generación del apunte sea **mucho más autónoma**. Ante cualquier vacío de contexto (código que el docente no verbalizó o diapositivas clave), el asistente puede extraer quirúrgicamente fotogramas en el segundo exacto mediante `extract_frame.py` o FFmpeg para inspeccionar la pantalla sin necesidad de que pauses tu trabajo para buscar y sacar capturas manualmente.

* **Resolución Automática con Video (MP4):** Si la clase dispone de video, ante una laguna de contexto en un timestamp `[HH:MM:SS]`, se extrae el fotograma correspondiente para recuperar la sintaxis real.
* **Extracción manual de soporte:**
  ```powershell
  python extract_frame.py "output/Clase 9.mp4" 01:42:15
  ```
  Genera la captura en `output/frames/Clase 9_01-42-15.jpg` lista para ser analizada.
* **Protocolo de Fallback (Solo MP3):** Si únicamente se dispone del audio MP3 o el contenido no fue proyectado en pantalla, el asistente pausará la redacción e indicará la marca de tiempo `[HH:MM:SS]` exacta para solicitar la información al usuario.

---

## Decisión de Diseño: Descarte de LLMs Locales (llama.cpp)

Se evaluó la posibilidad de integrar inferencia de modelos de lenguaje locales (LLMs de 3B a 8B mediante `llama.cpp`) para automatizar el 100% del ciclo de generación de apuntes en la máquina local. **Esta alternativa fue formalmente descartada** para la fase de síntesis final por las siguientes razones técnicas:

### 1. Cuello de botella de contexto y KV Cache (30.000 a 55.000 tokens)
* Una clase universitaria promedio (2 a 3 horas) genera transcripciones de entre 30.000 y 55.000 tokens.
* En `llama.cpp` corriendo en CPU, el preprocesamiento de ese volumen de prompt (*Prompt Processing* / Time-to-First-Token) requiere entre **15 y 30 minutos al 100% de uso de CPU** antes de comenzar a redactar.
* Además, el almacenamiento del *KV Cache* para 40.000+ tokens consume entre **4 y 8 GB adicionales de memoria RAM**, saturando los recursos del sistema mientras compite con las descargas o transcripciones de Whisper.

### 2. Alto riesgo de alucinación de código (*"Lost in the Middle"*)
* En asignaturas de programación, los docentes frecuentemente modifican fragmentos de código sin verbalizar la sintaxis exacta (*"cambiamos esta línea por lo que vimos la clase pasada"*).
* Los modelos chicos (< 8B) sufren de complacencia predictiva (*eagerness*): ante lagunas de información, **tienden a inventar código plausible** en vez de abstenerse.
* Un modelo chico carece de la metacognición para suspender la generación y solicitar: *"En [01:23:45] falta contexto, se requiere captura"*. Una sola línea de código alucinada en un controlador, migración o servicio invalida la utilidad del apunte para estudiar.

### 3. Necesidad de retroalimentación multimodal interactiva
* Para resolver las ambigüedades de código, el flujo exige inspeccionar capturas de pantalla (*screenshots*) sincronizadas por marca de tiempo, diapositivas en PDF y repositorios externos de GitHub.
* Los modelos locales de visión (VLMs) añaden una sobrecarga computacional prohibitiva en CPU, mientras que los asistentes avanzados o modelos de frontera procesan imágenes y código en segundos de manera nativa.

### 4. Arquitectura de responsabilidades adoptada (*Sweet Spot*)

| Fase del Flujo | Herramienta Asignada | Justificación |
| :--- | :--- | :--- |
| **Descarga y Recomposición** | `BBB-Scribe` (Playwright / FFmpeg) | Ejecución local rápida, automatizada y offline. |
| **Transcripción de Audio** | `faster-whisper` (Local CPU `int8`) | Máxima privacidad, sin costo de APIs, alta precisión con timestamps. |
| **Síntesis y Apuntes de Código** | Modelo de Frontera / Asistente IA | Cero alucinación de código, capacidad multimodal (screenshots) y pedagogía profunda. |

---

## Solución de Problemas Frecuentes

### 1. `Executable doesn't exist at ... playwright\chromium-...`
**Causa:** Falta descargar el binario de Chromium para Playwright.  
**Solución:** Ejecuta dentro del entorno virtual:
```powershell
playwright install chromium
```

### 2. `No se puede cargar el archivo Activate.ps1 porque la ejecución de scripts está deshabilitada`
**Causa:** Política de seguridad por defecto de Windows PowerShell.  
**Solución:** Habilita temporalmente la ejecución en tu sesión actual:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 3. La transcripción consume mucho uso de procesador (CPU)
**Causa:** Whisper utiliza multi-threading para acelerar la inferencia en CPU.  
**Solución:** Si estás realizando otras tareas pesadas en simultáneo o corriendo múltiples transcripciones en paralelo, utiliza el modelo `small` o `base`.

### 4. ¿Puedo compartir este proyecto sin subir los videos pesados?
**Sí.** El archivo `.gitignore` ya viene configurado para ignorar la carpeta `output/`, las carpetas `.venv/` y los ejecutables pesados de `bin/`. Puedes compartir el repositorio o la carpeta comprimida de forma ligera.
