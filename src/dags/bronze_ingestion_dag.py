import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from airflow import DAG
from airflow.utils.dates import days_ago
from datetime import timedelta
from airflow.providers.google.cloud.operators.functions import CloudFunctionInvokeFunctionOperator

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
REGION = os.environ["GCP_REGION"]
FUNCTION_ID = os.environ["EXTRACTOR_FUNCTION_ID"]

default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'bronze_data_ingestion',
    default_args=default_args,
    description='Extract raw files from Landing to BigQuery Bronze',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    tags=['ingestion', 'bronze'],
) as dag:
    
    # We pass the execution date formatted as YYYY/MM/DD using Airflow macros
    invoke_extractor = CloudFunctionInvokeFunctionOperator(
        task_id='invoke_bronze_extractor',
        project_id=PROJECT_ID,
        location=REGION,
        input_data={
            "execution_date": "{{ data_interval_end.strftime('%Y/%m/%d') }}"
        },
        function_id=FUNCTION_ID,
        gcp_conn_id='google_cloud_default',
    )
    
    invoke_extractor
