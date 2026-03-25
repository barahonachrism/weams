# Épica 3: Exposición de Resultados

Esta épica contempla la construcción, conexión y despliegue del Dashboard interactivo final para ser consultado por la audiencia de analistas y RRHH de la empresa de manera sencilla.

## Historia de Usuario 3.1: Configuración de Acceso a Dashboards
**Como** usuario de Recursos Humanos, 
**quiero** ver las habilidades Java con un score de 1 a 5 distribuidos por nivel de seniority, 
**para** ajustar los perfiles de búsqueda de la compañía de acuerdo con la información real de vacantes y mercado.

### Tareas
- [x] **Aprovisionamiento IAM para BI:** Configurar vía Terraform cuenta de lectura dedicada para BI (`SA-Looker`) con roles `dataViewer` y `jobUser` limitados al dataset Gold.
  - **Responsable:** DevOps
- [x] **Conexión BQ a Looker Studio:** Enlazar el reporte de Looker Studio con la capa Gold usando la cuenta de servicio configurada, verificando conectividad de origen sin errores.
  - **Responsable:** Ingeniero BI
- [x] **Validación Estratégica de Costos:** Garantizar y certificar que la arquitectura de tablero previene costes excesivos generados por consultas on-demand, certificando el uso y conexión eficiente a la capa materializada.
  - **Responsable:** Solutions Architect

---

## Historia de Usuario 3.2: Visualización Exhaustiva del Mercado
**Como** usuario de Recursos Humanos, 
**quiero** visualizar en la pantalla final de Looker Studio un listado total ordenado de todas las habilidades identificadas, 
**para** tener visibilidad incluso sobre tecnologías de nicho.

### Tareas
- [x] **Maquetado y UI/UX del Dashboard:** Construir los gráficos, scorecards y filtros visuales dentro de Looker Studio, presentando en una escala de 1-5 la métrica de relevancia de las tecnologías Java.
  - **Responsable:** Ingeniero BI
- [x] **Aplicar Regla de Exhaustividad de Listas:** Ajustar todos los controles de tabla o lista dentro de Looker Studio para eliminar cualquier restricción estática a un "Top 10" nativa de la herramienta.
  - **Responsable:** Ingeniero BI
- [x] **Filtros por Nivel de Especialidad:** Habilitar controles visuales que dejen cruzar y categorizar por `Junior`, `Senior` y `Arquitecto`.
  - **Responsable:** Ingeniero BI

---

## Historia de Usuario 3.3: Despliegue CI/CD y Pruebas End-to-End
**Como** Analista de Datos y Stakeholder de Negocio, 
**quiero** garantizar que los pipelines en GCP estén implementados de extremo a extremo, 
**para** ejecutar el flujo analítico completo desde el volcado de la Landing Zone hasta el modelo validado en Gold de manera orquestada.

### Tareas
- [x] **Despliegue Continuo (CI/CD):** Implementar la logística necesaria (Cloud Build, GitHub Actions o comandos de GCP) para empaquetar y subir el código Python de `extractors`, `transformers` y las lógicas `dags` directamente hacia las ubicaciones productivas de Cloud Functions y Cloud Composer.
  - **Responsable:** DevOps
- [x] **Prueba de Integración Real (End-to-End):** Insertar un archivo nuevo de prueba en la capa Landing (GCS), invocar manualmente la Cloud Function, esperar el procesamiento de Dataflow a través del DAG, y validar la aparición del puntaje normalizado en la tabla `gold.skills_scoring`.
  - **Responsable:** Data Engineer / Solutions Architect
