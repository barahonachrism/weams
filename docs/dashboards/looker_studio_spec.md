# Especificación de Diseño: Looker Studio Dashboard
**Proyecto:** Java Developer Skills DWH  
**Responsable:** Ingeniero BI  
**Fuente de Datos:** Tabla `joi-jinko.gold.skills_scoring`

## 1. Conexión de Datos (Data Source)
1. Entrar a [Looker Studio](https://lookerstudio.google.com/).
2. Crear un nuevo **Data Source**.
3. Seleccionar el conector **BigQuery**.
4. Autorizar utilizando el método de cuenta de servicio (service account) subiendo la llave (JSON) de `sa-looker@joi-jinko.iam.gserviceaccount.com`. *(Esto garantiza política de control de acceso seguro y solo lectura a Gold).*
5. Seleccionar Project: `joi-jinko` -> Dataset: `gold` -> Table: `skills_scoring`.

## 2. Tipado y Clasificación de Campos
En la vista previa de edición del Data Source, ajustar los tipos de datos:
- `skill_name`: Tipo `Texto` (Dimensión).
- `seniority_level`: Tipo `Texto` (Dimensión).
- `frequency`: Tipo `Número` (Métrica). Agregación: `Suma`.
- `demand_score_1_to_5`: Tipo `Número` (Métrica). Agregación: `Promedio` o `Máx` (como todos los scores de una misma fecha son iguales por tecnología, promedio es seguro).
- `learning_url`: Tipo `URL` (Dimensión).
- `processed_timestamp`: Tipo `Fecha y Hora` (Dimensión Fecha Default).

## 3. Disposición del Layout UI/UX
Configurar el lienzo a panorámico (Resolución 16:9). El tema sugerido es **Dark Mode (Glassmorphism)** con acentos azules o morados para dar aspecto premium tech, en concordancia con un proyecto de Data Engineering en GCP.

### 3.1. Selector de Filtros (Top Bar)
- **Filtro tipo Dropdown (Lista Desplegable):** Para la dimensión `seniority_level`. Permite fijar la vista seleccionando explícitamente `Junior`, `Senior`, o `Arquitecto`, recargando la tabla principal en cascada.
- **Filtro de Rango de Fechas:** Apuntando a `processed_timestamp` configurado en "Últimos 30 días".

### 3.2. Gráfico Principal: Matriz de Calor / Tabla
- **Tipo de Gráfico:** "Tabla con mapas de calor" o "Gráfico de Barras Horizontales".
- **Dimensión Principal:** `skill_name`.
- **Métrica 1:** `demand_score_1_to_5` (Mostrar en formato numérico con barras de datos alineadas. Es esencial para mostrar la **"escala 1-5"** solicitada corporativamente).
- **Métrica 2:** `frequency` (Para referencia del reclutador).
- **Dimensión 2 (Columna Extra):** `learning_url` (Looker Studio lo pintará como hipervínculo clickeable que redirige a recursos sugeridos).

> [!WARNING]
> **Regla de Exhaustividad de Negocio:** Asegúrate de ir a la configuración de datos de esta Tabla y en **Filas por página** escoger el número máximo (`100` o más) en lugar de la restricción estática nativa clásica del Top 10. La gerencia pidió expresamente poder revisar tecnologías de cola larga o nicho (Exhaustividad total).

### 3.3. Scorecards de Resumen
Tres tarjetas pequeñas en la parte superior reflejando:
1. Total de Skills analizadas distintas (`COUNT_DISTINCT(skill_name)`).
2. Nivel de Seniority más demandado (Métrica `frequency` dimensión `seniority_level` orden descendente).
3. Fecha de última actualización de la Base de Datos.
