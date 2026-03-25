# Java Developer Skills - GCP Data Warehouse Pipeline

Este proyecto implementa analítica de datos en Google Cloud Platform (GCP) para revelar las competencias esenciales (skills) que requieren los desarrolladores de software enfocados en Java (Niveles Junior, Senior, Arquitecto).

## Componentes de la Arquitectura

El flujo end-to-end utiliza servicios Serverless y analíticos nativos de Google:

1. **Landing Zone (GCS)**: Contenedor para los archivos multimedia o documentos originales recolectados (`.pdf`, `.mp4`, `.mp3`, `.doc`, `.xls`, `.ppt`).
2. **Capa Bronze (BigQuery)**: Una tabla transicional dentro de BigQuery. Mediante un proceso de transcripción y extracción, los archivos de la Landing Zone son procesados, almacenando aquí el nombre del archivo, su ruta en el bucket y su contenido extraído en formato estructurado `.json`.
3. **Procesamiento Silver (Dataflow)**: Pipelines de transformación que leen la información JSON directamente de la tabla Bronze de BigQuery, normalizan skills y aplican cruces con demandas del negocio, depositándolo en tablas base normalizadas.
4. **Modelado Gold (BigQuery)**: Views o tablas analíticas en BQ, escalando las importancias de las habilidades de 1 a 5. Los datos se ordenan del skill más demandado al menos demandado, sin límites.
5. **Orquestación (Cloud Composer)**: Orquesta la activación de flujos batch y actualizaciones entre GCS, extracción a Bronze, Dataflow hacia Silver y BQ Gold.
6. **Reporte (Looker Studio)**: Dashboard final con conexión a BigQuery diseñado para los Key Users.

---

## Instrucciones para el Despliegue

### 1. Requisitos Previos (Prerequisites)
- SDK de Google Cloud (`gcloud`) instalado apuntando a tu ambiente operativo y cuota activa.
- [Terraform CLI](https://developer.hashicorp.com/terraform/downloads) >= 1.0.
- Cuenta de Servicio de aprovisionamiento con roles suficientes para IAM, Storage, BigQuery, Dataflow, y Composer.

### 2. Aprovisionamiento de Infraestructura (DevOps)
La carpeta `/terraform` del proyecto se encarga de dar de alta la infraestructura.

**Configuración de `gcloud`:**
1. Autentícate y configura tu cuenta: `gcloud auth application-default login` y `gcloud config set account [TU_CUENTA]`.
2. Configura tu proyecto activo: `gcloud config set project [PROJECT_ID]`.
3. Configura tu región por defecto: `gcloud config set compute/region [REGION]`.
4. Define el proyecto para cuotas: `gcloud auth application-default set-quota-project [PROJECT_ID]`.

**Despliegue de Terraform:**
1. Ve a la carpeta `terraform/`.
2. Renombra las variables necesarias en `terraform.tfvars`.
3. Instala los proveedores e inicializa el repo: `terraform init`.
4. Revisa los recursos a crear: `terraform plan`.
5. Aplica la infraestructura: `terraform apply -auto-approve`. 

### 3. Búsqueda y Carga a Landing (Investigador)
1. Buscar y reunir fuentes `.pdf`, `.mp4`, `.doc`, etc., con análisis de demanda o vacantes.
2. Subir estos archivos físicos originales a tu bucket de GCP `gs://[PROJECT_ID]-landing`.

### 4. Despliegue de Código (Data Engineer)
Tu código del flujo residirá típicamente en directorios como `/src/beam_pipelines` o `/dags`.
1. Mueve/Publica los archivos de extracción hacia Bronze y los `.py` de Cloud Composer DAG a la carpeta asignada en GCS.
2. Automáticamente Airflow orquestará el flujo completo: Transcripción de Archivos Landing -> Tabla Bronze -> Pipeline Beam a capa Silver -> Vista Gold.

### 5. Configuración del Reporte (Ingeniero BI)
1. Ingresa a `lookerstudio.google.com`.
2. Crea un Reporte en Blanco y selecciona como Origin "BigQuery".
3. Vincula y autoriza al proyecto respectivo, dataset `gold` y la tabla rankeada.
4. Modela visualmente la ponderación, controles de filtro y la interfaz final UI/UX.
