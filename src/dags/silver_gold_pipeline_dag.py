import os
from airflow import DAG
from airflow.utils.dates import days_ago
from datetime import timedelta
from airflow.providers.google.cloud.operators.dataflow import DataflowCreatePythonJobOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "joi-jinko")
REGION = "us-central1"
GCS_BUCKET = f"{PROJECT_ID}-dataflow-staging"

default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

GOLD_SQL_QUERY = f"""
-- DDL for Gold Layer
CREATE OR REPLACE TABLE `{PROJECT_ID}.gold.skills_scoring`
PARTITION BY DATE(processed_timestamp)
CLUSTER BY seniority_level, skill_name
AS
WITH skill_counts AS (
    SELECT 
        skill_name,
        seniority_level,
        COUNT(*) as frequency,
        MAX(processed_timestamp) as processed_timestamp
    FROM `{PROJECT_ID}.silver.normalized_skills`
    GROUP BY skill_name, seniority_level
),
max_freq AS (
    SELECT 
        seniority_level, 
        MAX(frequency) as max_f
    FROM skill_counts
    GROUP BY seniority_level
)
SELECT 
    s.skill_name,
    s.seniority_level,
    s.frequency,
    CAST(ROUND((s.frequency / m.max_f) * 4) + 1 AS INT64) as demand_score_1_to_5,
    s.processed_timestamp
FROM skill_counts s
JOIN max_freq m ON s.seniority_level = m.seniority_level
"""

DELETE_SILVER_QUERY = f"""
DELETE FROM `{PROJECT_ID}.silver.normalized_skills`
WHERE execution_date = '{{{{ data_interval_end.strftime('%Y-%m-%d') }}}}'
"""

with DAG(
    'silver_gold_transformation',
    default_args=default_args,
    description='Pipeline for Bronze->Silver->Gold transformation',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    tags=['transformation', 'silver', 'gold'],
) as dag:
    
    clean_silver_partition = BigQueryInsertJobOperator(
        task_id="clean_silver_partition",
        configuration={
            "query": {
                "query": DELETE_SILVER_QUERY,
                "useLegacySql": False,
            }
        },
        location="US",
    )

    bronze_to_silver_dataflow = DataflowCreatePythonJobOperator(
        task_id="bronze_to_silver_dataflow",
        # Reference relative to dags folder if uploaded to Composer bucket
        py_file="transformers/bronze_to_silver.py", 
        job_name="bronze-to-silver-{{ data_interval_end.strftime('%Y%m%d') }}",
        options={
            'project_id': PROJECT_ID,
            'execution_date': "{{ data_interval_end.strftime('%Y-%m-%d') }}",
            'bronze_table': 'bronze.raw_transcriptions',
            'silver_table': 'silver.normalized_skills',
            'dlq_table': 'silver.normalized_skills_dlq',
            'taxonomy_table': 'silver.skills_taxonomy',
            'tempLocation': f'gs://{GCS_BUCKET}/temp',
            'stagingLocation': f'gs://{GCS_BUCKET}/staging',
            'runner': 'DataflowRunner',
            'region': REGION
        },
        location=REGION,
        wait_until_finished=True
    )
    
    update_gold_layer = BigQueryInsertJobOperator(
        task_id="update_gold_layer",
        configuration={
            "query": {
                "query": GOLD_SQL_QUERY,
                "useLegacySql": False,
            }
        },
        location="US",
    )
    
    clean_silver_partition >> bronze_to_silver_dataflow >> update_gold_layer
