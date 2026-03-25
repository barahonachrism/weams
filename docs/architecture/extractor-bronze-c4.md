# Arquitectura del Extractor y Transcriptor (Capa Bronze)

Este documento describe la arquitectura C4 (Context, Container, Component) para el sistema de extracción y transcripción de datos crudos (Landing Zone en GCS) hacia datos semi-estructurados (JSON en BigQuery Capa Bronze), según los requerimientos de la Épica 1.

## Nivel 1: Diagrama de Contexto de Sistema (System Context)

```mermaid
C4Context
    title Diagrama de Contexto de Sistema - Ingesta Raw a Bronze

    Person(data_analyst, "Analista de Datos", "Analiza las tendencias y demandas tecnológicas.")
    System_Ext(external_sources, "Fuentes de Mercado", "Sitios de empleo, blogs, videos sobre Java (.pdf, .mp4, etc.)")
    
    System(weams_platform, "Weams Data Platform", "Plataforma analítica que ingesta, transcribe y estructura los datos crudos para análisis en GCP.")
    
    Rel(external_sources, weams_platform, "Los archivos crudos son recolectados manual/automáticamente y enviados a")
    Rel(data_analyst, weams_platform, "Consulta datos transcritos y estructurados JSON en BigQuery")
```

## Nivel 2: Diagrama de Contenedores (Containers)

```mermaid
C4Container
    title Diagrama de Contenedores - Capa Landing y Bronze

    Person(data_engineer, "Data Engineer / Orchestrator")
    
    System_Boundary(gcp_boundary, "Google Cloud Platform") {
        Container(gcs_landing, "Landing Zone", "Cloud Storage", "Almacena los archivos crudos originales (.pdf, .mp4, etc.) particionados por fecha.")
        Container(cloud_composer, "Orquestador", "Cloud Composer (Airflow)", "Coordina el flujo, detecta nuevos archivos en Landing y dispara la extracción.")
        Container(extractor_function, "Extractor & Transcriptor", "Cloud Function (Python 3.11)", "Servicio sin servidor que lee los documentos y videos, extrae el texto usando APIs de ML y lo transforma a JSON.")
        ContainerDb(bq_bronze, "Bronze Layer", "BigQuery", "Almacena los contenidos estructurados en JSON dentro de la tabla raw_transcriptions.")
    }
    
    Rel(data_engineer, cloud_composer, "Despliega y monitorea DAGs")
    Rel(cloud_composer, gcs_landing, "Detecta objetos nuevos/Trigger")
    Rel(cloud_composer, extractor_function, "Invoca proceso de extracción de archivos (HTTP/Event)")
    Rel(extractor_function, gcs_landing, "Lee payload y archivos crudos")
    Rel(extractor_function, bq_bronze, "Inserta registros estructurados (JSON) vía Streaming/Batch")
```

## Nivel 3: Diagrama de Componentes (Components)

```mermaid
C4Component
    title Diagrama de Componentes - Extractor & Transcriptor (Cloud Function)
    
    Container_Boundary(cf_boundary, "Cloud Function: Extractor (Python 3.11)") {
        Component(api_handler, "API / Event Handler", "Flask / Functions Framework", "Recibe la solicitud de orquestación (Composer) con el GCS URI a procesar.")
        Component(file_reader, "File Reader Service", "Python Cloud Storage Client", "Lee o descarga el contenido crudo desde el bucket de Landing.")
        Component(transcriber, "Media Transcriber Service", "Python (Document AI, Speech-to-Text)", "Aplica técnicas de NLP y OCR o transcripción de audio dependiendo de la extensión del archivo (.pdf, .mp4).")
        Component(json_formatter, "JSON Formatter", "Python", "Estructura el texto final y crea el esquema JSON de metadatos (file_name, file_path, extracted_content, timestamp).")
        Component(bq_writer, "BigQuery Writer", "Python BigQuery Client", "Escribe la salida estructurada a la tabla `raw_transcriptions` en la Capa Bronze.")
    }
    
    Rel(api_handler, file_reader, "Delega URI del archivo")
    Rel(file_reader, transcriber, "Pasa bytes del contenido y extensión")
    Rel(transcriber, json_formatter, "Entrega texto extraído en crudo")
    Rel(json_formatter, bq_writer, "Entrega payload estructurado JSON")
```

## Decisiones Técnicas Evaluadas
- **Despliegue Serverless**: El Extractor utiliza Cloud Functions asegurando costos bajo demanda y soporte nativo Python 3.11, en lugar de un cluster dedicado.
- **Identidades Administradas**: Se usan de forma específica `sa-bronze-extractor` para la función, aislando permisos (Storage Object Admin y BQ Data Editor únicamente).
- **Tipado BigQuery**: El esquema en Bronze usa el tipo de dato `JSON` para `extracted_content`, permitiendo flexibilidad sin rediseños del esquema relacional en Bronze.
- **Idempotencia**: El orquestador o la función debe verificar si el `file_path` ya está registrado en `raw_transcriptions` antes de la inserción, de cara a re-procesamientos.
