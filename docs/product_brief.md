# Product Brief: Java Developer Skills Analytics Pipeline

## 1. Visión del Producto
Proveer una solución analítica integral que identifique y clasifique las competencias técnicas (skills) requeridas para desarrolladores Java en distintos niveles de seniority (Junior, Senior, Arquitecto). Esto dotará a los equipos de reclutamiento, recursos humanos y a los candidatos con métricas claras y cuantificables sobre la demanda tecnológica del mercado de manera automatizada.

## 2. Objetivos del Negocio
- **Extracción Multiformato Automatizada:** Procesar y extraer habilidades de archivos heterogéneos (como PDFs, videos MP4, audios, documentos DOC/XLS) centralizados en Google Cloud Storage (Landing Zone).
- **Procesamiento Escalable:** Implementar un Data Warehouse Serverless en Google Cloud (BigQuery, Dataflow, Cloud Composer) capaz de transformar datos en crudo a información de negocio accionable (modelado Bronze, Silver, Gold).
- **Tablero Estratégico Exhaustivo:** Diseñar un dashboard en Looker Studio orientado a Key Users que presente las habilidades detectadas con un puntaje de relevancia (score de 1 a 5) y muestre un ordenamiento completo exhaustivo.

## 3. Principales Épicas e Historias de Usuario

*(Nota: Las historias detalladas y requerimientos técnicos continuarán su desglose como tareas priorizadas dentro de la carpeta `stories/` del proyecto, siguiendo la definición de entregables).*

### Épica 1: Ingesta y Almacenamiento Raw
- **Historia 1.1:** Como Investigador, quiero disponer de una Landing Zone en Google Cloud Storage para poder subir fácilmente las fuentes recolectadas (`.pdf`, `.mp4`, etc.) sobre vacantes y mercado.
- **Historia 1.2:** Como Analista de Datos, quiero que los archivos crudos se transcriban a un formato estructurado (`.json`) y se depositen en una tabla Bronze en BigQuery, para poder analizar contenido originalmente no estructurado.

### Épica 2: Transformación Analítica y Normalización
- **Historia 2.1:** Como Arquitecto de Datos, quiero que pipelines en Dataflow procesen los registros extraídos desde Bronze, para estandarizar las habilidades a través de una taxonomía de lenguajes de programación y generar la capa Silver.
- **Historia 2.2:** Como Desarrollador de BI, quiero consumir vistas/tablas sobre la capa analítica Gold en BigQuery que dispongan del score calculado de 1 a 5 por cada habilidad de mercado.

### Épica 3: Exposición de Resultados
- **Historia 3.1:** Como usuario de Recursos Humanos, quiero ver las habilidades Java con un score de 1 a 5 distribuidos por nivel de seniority, para ajustar los perfiles de búsqueda de la compañía de acuerdo con la información real de vacantes y mercado.
- **Historia 3.2:** Como usuario de Recursos Humanos, quiero visualizar en la pantalla final de Looker Studio un listado total ordenado de todas las habilidades identificadas, para tener visibilidad incluso sobre tecnologías de nicho.

## 4. Criterios de Aceptación Globales
- **Integridad Taxonómica:** Los cruces en la capa analítica deben considerar obligatoriamente la regla de negocio para la taxonomía del lenguaje (diferenciando plataformas, frameworks y versiones cuando sea pertinente).
- **Exhaustividad de Vista Final:** La pantalla y tableros en Looker Studio deben proveer un ordenamiento total en todas las listas, garantizando una visibilidad completa de los resultados.
- **Métrica de Impacto Escalar:** El modelo analítico Gold y el nivel visual de Looker Studio deben mostrar clara y numéricamente la métrica de relevancia en el rango definido (1 a 5).
- **Orquestación End-to-End:** Todo ciclo (desde la ingesta en GCS, hasta la carga final en las vistas Gold) será orquestado por DAGs ejecutados en Cloud Composer, los cuales se activarán de forma bajo demanda de acuerdo a la necesidad.
