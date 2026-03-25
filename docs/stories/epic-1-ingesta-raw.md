# Épica 1: Ingesta y Almacenamiento Raw

Esta épica agrupa las historias de usuario relacionadas con la ingesta inicial de información del mercado sobre skills de desarrolladores Java y su almacenamiento en crudo dentro de Google Cloud Storage (Landing Zone) y posterior transcripción hacia BigQuery (Bronze).

## Historia de Usuario 1.1: Landing Zone Setup & Carga de Archivos
**Como** Investigador, 
**quiero** disponer de una Landing Zone en Google Cloud Storage 
**para** poder subir fácilmente las fuentes recolectadas (`.pdf`, `.mp4`, etc.) sobre vacantes y mercado en crudo.

### Tareas
- [x] **Aprovisionar Infraestructura GCS:** Crear vía Terraform el bucket de Cloud Storage particionado por fecha (`gs://[PROJECT_ID]-landing/YYYY/MM/DD/archivos`) para la Landing Zone.
  - **Responsable:** DevOps
- [x] **Validar Configuración IaC:** Realizar Code Review del PR de infraestructura (HCL) validando políticas y nombres de buckets.
  - **Responsable:** Solutions Architect
- [x] **Recolección Activa de Información:** Escanear el entorno y buscar fuentes web y corporativas sobre tendencias tecnológicas, análisis de demanda y vacantes de Java. Se deben considerar múltiples formatos comprobados (`.pdf`, `.mp4`, `.mp3`, `.doc`, `.xls`, `.ppt`, `.txt`, `.md`, `.html`, `.htm`, `.json`, `.xml`, `.csv`, etc.).
  - **Responsable:** Investigador
- [x] **Carga a Landing Zone:** Depositar de forma organizada toda la información valiosa recolectada hacia el bucket de Google Cloud Storage (Landing Zone) habilitado para dar inicio al flujo analítico.
  - **Responsable:** Investigador

---

## Historia de Usuario 1.2: Capa Bronze - Extractor y Transcriptor Raw a Estructurado
**Como** Analista de Datos, 
**quiero** que los archivos crudos se transcriban a un formato estructurado (`.json`) y se depositen en una tabla Bronze en BigQuery, 
**para** poder analizar contenido originalmente no estructurado.

### Tareas
- [x] **Aprovisionar BigQuery Bronze:** Definir e implementar en Terraform el dataset y tabla Bronze inicial en BigQuery, junto con las identidades administradas.
  - **Responsable:** DevOps
- [x] **Desarrollo de Extracción:** Crear y desplegar la lógica de Cloud Function / API para transcribir y extraer texto de medios crudos (Video, Documentos) a formato estructural JSON insertando registros en Bronze.
  - **Responsable:** Data Engineer
- [x] **Orquestación Básica:** Integrar el trigger de la extracción hacia Bronze en el entorno de Airflow/Composer.
  - **Responsable:** Data Engineer
- [x] **Revisión de Arquitectura:** Validar el diseño del Extractor en Google Cloud y revisar PRs asegurando que se extraigan los formatos requeridos.
  - **Responsable:** Solutions Architect
