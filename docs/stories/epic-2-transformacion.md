# Épica 2: Transformación Analítica y Normalización

Esta épica agrupa las tareas para mover, transformar y normalizar los datos en BQ Bronze a una capa estructurada Silver, y por último precalcular las agregaciones necesarias en la capa Gold mediante modelos analíticos listos para consumir.

## Historia de Usuario 2.1: Pipeline de Normalización Dataflow (Bronze to Silver)
**Como** Arquitecto de Datos, 
**quiero** que pipelines en Dataflow procesen los registros extraídos desde Bronze, 
**para** estandarizar las habilidades a través de una taxonomía de lenguajes de programación y generar la capa Silver.

### Tareas
- [x] **Aprovisionamiento IAM y Composer:** Levantar vía Terraform el entorno de Cloud Composer (Airflow) y las Service Accounts (`SA-Composer`, `SA-Dataflow`) aplicando Least Privilege.
  - **Responsable:** DevOps
- [x] **Desarrollo de Pipeline en Dataflow:** Escribir y probar en Python 3.11 el cluster y la pipeline Beam basada en plantillas de Dataflow, que ejecute la lectura desde Bronze, normalización de taxonomías y escritura a tabla Silver en BQ.
  - **Responsable:** Data Engineer
- [x] **Desarrollo de DAGs (Composer):** Escribir DAG en Airflow para orquestar la transformación Bronze->Silver asegurando un diseño idempotente y manejo granular de fallas.
  - **Responsable:** Data Engineer
- [ ] **Evaluación de Código (Beam y DAGs):** Revisar PRs de Python asegurando uso de versión 3.11, control de excepciones robusto (dead letter queues), diseño idempotente y justificación de uso del Dataflow Serverless.
  - **Responsable:** Solutions Architect

---

## Historia de Usuario 2.2: Modelado Analítico de Capa Gold
**Como** Desarrollador de BI, 
**quiero** consumir vistas/tablas sobre la capa analítica Gold en BigQuery que dispongan del score calculado de 1 a 5 por cada habilidad de mercado,
**para** facilitar el consumo y no encarecer consultas continuas.

### Tareas
- [x] **Definición Estructural de Tablas/Vistas Gold:** Diseñar y estructurar la capa Gold implementando BigQuery Materialized Views o flujos SQL tabulados sobre modelo de estrella (Star Schema).
  - **Responsable:** Data Engineer
- [x] **Modelado Agregado (Ponderaciones):** Elaborar script SQL para pre-calcular relevancia/score de skills (escala 1-5) clasificándolos por nivel (Junior, Senior, Arquitecto).
  - **Responsable:** Data Engineer
- [ ] **Revisión de Clustering y Particionamiento:** Validar las políticas de optimización de datos en Gold (particionamiento por timestamp y clustering por prioridades analíticas como `skill_name` y `seniority_level`).
  - **Responsable:** Solutions Architect
