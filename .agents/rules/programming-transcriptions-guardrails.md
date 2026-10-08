# Directiva: Integridad de Código, Resolución Visual y Generación de Apuntes

Al generar apuntes técnicos o explicaciones a partir de transcripciones de clases de programación:

1. **Cero Alucinación de Código:**
   - Si el profesor no verbaliza la línea de código completa, omite sintaxis crítica o hace referencia visual a cambios en pantalla ("aquí cambié esto", "miren esta función", etc.), **queda estrictamente prohibido inventar o asumir el código**.

2. **Detección de Disponibilidad de Medios (MP4 vs. MP3):**
   - Verificar si en la carpeta `output/` existe el archivo de video (`.mp4`) correspondiente a la clase o únicamente el audio (`.mp3`).

3. **Resolución Automática con Extracción de Fotogramas (Si hay Video MP4):**
   - Al detectar un vacío de contexto en un timestamp determinado (`[HH:MM:SS]`), recurrir a la extracción de uno o varios frames del video en ese instante temporal utilizando FFmpeg o `extract_frame.py`.
   - Inspeccionar visualmente la captura resultante (editor de código, consola, diapositiva) para reconstruir el código fidedigno e incorporarlo al apunte sin interrumpir al usuario innecesariamente.

4. **Protocolo de Interrupción y Solicitud al Usuario (Si solo hay MP3 o falta material):**
   - Si únicamente se cuenta con archivo de audio (`.mp3`), o si en el video la pantalla no muestra el código en cuestión (ej. se discutía código de un alumno no proyectado o diapositivas externas):
     1. **Detener inmediatamente** la redacción de esa sección del apunte.
     2. Indicar con precisión el **timestamp exacto** (`[HH:MM:SS]`) de la transcripción donde ocurre la omisión.
     3. Solicitar al usuario una captura de pantalla (screenshot) o el material de apoyo (PDF, repositorio del docente/alumno) para continuar.

---

## 5. Protocolo de Generación de Apuntes Académicos

Cuando el usuario solicite generar un apunte a partir de una transcripción:

1. **Parámetros de Entrada Obligatorios:**
   - **Ruta de destino:** Se debe contar con la ruta exacta donde se guardará el archivo `.md` (ej. `Docs/Clase XX.md`). Si no fue indicada, solicitarla antes de escribir.
   - **Ruta de documentación adjunta:** Se debe contar con la ruta del material complementario de cátedra (diapositivas, PDFs, guías de laboratorio) para contrastar, enriquecer y verificar la fidelidad técnica del contenido dictado.

2. **Estructura y Jerarquía del Apunte:**
   - **Introducción de Expectativas Docentes:** Abrir el apunte con un resumen conciso de los objetivos pedagógicos de la clase y las competencias que el docente espera que el alumno incorpore.
   - **Desarrollo Temático Depurado:** Desarrollar exhaustivamente todos los temas dictados por el profesor, eliminando divagaciones, dudas temporales, repeticiones innecesarias o errores verbales que el docente haya corregido durante la sesión.
   - **Código Didáctico y Comentado:** Todo ejemplo técnico o demostración práctica debe presentarse en bloques de código completos y limpios, incorporando comentarios explicativos línea a línea dentro del propio código que justifiquen el porqué de cada sentencia.
