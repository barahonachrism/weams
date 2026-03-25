# Deuda Técnica - Extractor Bronze

**Contexto:**
Durante el proceso de Code Review del código base de `bronze_extractor` (Cloud Function `main.py`) se encontraron los siguientes puntos de deuda técnica y deficiencias con respecto a la arquitectura diseñada y buenas prácticas como *Solutions Architect*:

### DT-1: Falta de Idempotencia en Inserción de Datos a BigQuery (Crítico)
* **Problema:** La función realiza inserciones directas vía `insert_rows_json`. Si por un fallo el orquestador repite el proceso sobre una misma fecha o un archivo falla a la mitad, se producirán duplicados masivos.
* **Solución Propuesta:** Implementar un mecanismo de borrado previo (o sentencias `MERGE`) en la tabla `raw_transcriptions` para la fecha `execution_date` antes del lote principal, asegurando total idempotencia.

### DT-2: Incompatibilidad de Formatos y Uso Excesivo de Memoria (Crítico)
* **Problema:** El código hace uso de `blob.download_as_text()` iterando todos los archivos de GCS cargando su contenido a la RAM de la función. Esto fallará inexorablemente al intentar leer videos `.mp4` o documentos PDF, causando *Out-of-Memory (OOM)* o un error de decodificación de texto.
* **Solución Propuesta:** Utilizar la URI del blob en GCS (`gs://...`) y pasarlo a las APIs de procesamiento correspondientes (por ejemplo, Google Cloud Speech-to-Text / Video Intelligence para medios, y Document AI para PDF) para delegar y ejecutar el trabajo pesado de transcribir sin cargar el binario entero a la función. Agregar dichas dependencias en `requirements.txt`.

### DT-3: Manejo de Excepciones Silencioso e Incompleto (Medio)
* **Problema:** Dentro del bucle `for`, los errores al intentar procesar un archivo se tragan silenciosamente (`except Exception as e: print...`). Al terminar, si al menos procesó otros archivos, se devuelve un estado HTTP 200 existoso. Airflow asumirá conclusión total erradamente.
* **Solución Propuesta:** Implementar un Dead Letter Queue y recolectar qué archivos fallaron para devolverlos en un payload HTTP de error, u forzar el fallo (Fail-Fast) elevando la excepción hacia el orquestador.

### DT-4: Acoplamiento de Componentes y Variables Hardcodeadas (Bajo)
* **Problema:** Existe un acoplamiento donde toda la lógica se desarrolla en `extract_to_bronze()`. Valores como `DATASET_ID` y `TABLE_ID` están *hardcodeados* bloqueando despliegues multi-ambiente (dev/staging/prod).
* **Solución Propuesta:** Extraer las variables globales para que sean cargadas vía variables de entorno (`os.environ`), separando la lógica en un esquema de clases o archivos modulares que representen los componentes detectados de la arquitectura C4 y mejoren la legibilidad.

### DT-5: Ausencia de Aislamiento de Entorno (Virtual Env) y Variables Locales (Bajo)
* **Problema:** El entorno de desarrollo local carece de aislamiento. No hay especificación de crear entornos virtuales (`venv`, `conda`) ni un mecanismo estandarizado para pruebas locales con variables de entorno (`.env`).
* **Solución Propuesta:** Exigir que los desarrolladores usen un entorno virtual y un archivo `.env` o `.yaml` (soportado por functions-framework) para asegurar consistencia entre las variables de GCP y la prueba local.

---

## Tareas de Refactorización (Deuda Técnica)
- [x] **Resolver DT-1 (Idempotencia en Bronze):** Sustituir inserciones directas por sentencias MERGE o borrado previo por fecha, garantizando idempotencia desde el orquestador.
  - **Responsable:** Data Engineer
- [x] **Resolver DT-2 (Procesamiento Serverless sin RAM OOM):** Refactorizar código para evitar descargar archivos masivos en memoria. Utilizar URI (`gs://...`) y enviarlas directamente a Google Cloud Speech-to-Text / Document AI.
  - **Responsable:** Data Engineer
- [x] **Resolver DT-3 (Excepciones y DLQ):** Implementar patrón Dead Letter Queue y recolectar transacciones fallidas, implementando *fail-fast* o reportando estado HTTP 500 al orquestador en fallos mayores.
  - **Responsable:** Data Engineer
- [x] **Resolver DT-4 (Desacoplar Constantes):** Extraer variables como `DATASET_ID` y modularizar el script inicial a clases siguiendo lineamientos C4 de componentes.
  - **Responsable:** Data Engineer
- [x] **Resolver DT-5 (Entornos Virtuales y `.env`):** Estandarizar el uso de virtual environments de Python y archivos de variables de entorno para correr y probar la función en el equipo local de desarrollo.
  - **Responsable:** Data Engineer
- [ ] **Code Review Integral de Refactor:** Revisión de PR con la reestructuración completa del `bronze_extractor` validando eficiencia real y mitigación técnica.
  - **Responsable:** Solutions Architect
