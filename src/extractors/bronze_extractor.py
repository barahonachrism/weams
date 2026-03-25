import functions_framework
import json
import os
import traceback
from datetime import datetime
from google.cloud import storage, bigquery

# Try to load local .env if python-dotenv is available (DT-5)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# (DT-4) Constants from Environment
PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
BUCKET_NAME = os.environ.get("BUCKET_NAME", f"{PROJECT_ID}-landing")
DATASET_ID = os.environ["DATASET_ID"]
TABLE_ID = os.environ["TABLE_ID"]

class BronzeExtractor:
    def __init__(self):
        self.storage_client = storage.Client(project=PROJECT_ID)
        self.bq_client = bigquery.Client(project=PROJECT_ID)
        self.table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    def ensure_idempotency(self, exec_date: str):
        """ (DT-1) Deletes records for the given execution date before inserting new ones. """
        query = f"""
            DELETE FROM `{self.table_ref}`
            WHERE file_path LIKE '%/{exec_date}/%'
        """
        try:
            query_job = self.bq_client.query(query)
            query_job.result()  # Wait for the job to complete
            print(f"Idempotency check: Deleted previous records for {exec_date}")
        except Exception as e:
            print(f"Warning: Idempotency delete failed or table not found: {e}")

    def process_file(self, blob) -> dict:
        """ (DT-2) Serverless Processing: Process without loading heavy files to RAM if possible """
        file_name = blob.name.split('/')[-1]
        file_ext = file_name.split('.')[-1].lower() if '.' in file_name else ''
        
        extracted_json = None
        
        if file_ext in ['mp4', 'pdf', 'mp3', 'doc', 'ppt']:
            # For media/heavy files, we would pass the URI to Speech-to-Text / Document AI
            # Here we simulate that by just storing the URI in the structured format
            extracted_json = json.dumps({
                "raw_text": f"[PROCESSED BY API] External processing requested for {file_name}",
                "source_uri": f"gs://{BUCKET_NAME}/{blob.name}",
                "format": file_ext
            })
        else:
            # For small text/json files, download as text
            content_str = blob.download_as_text()
            if file_ext == 'json':
                try:
                    extracted_json = json.dumps(json.loads(content_str))
                except json.JSONDecodeError:
                    extracted_json = json.dumps({"raw_text": content_str})
            else:
                extracted_json = json.dumps({"raw_text": content_str})
                
        return {
            "file_name": file_name,
            "file_path": f"gs://{BUCKET_NAME}/{blob.name}",
            "extracted_content": extracted_json,
            "ingestion_timestamp": datetime.utcnow().isoformat()
        }

    def run(self, exec_date: str):
        self.ensure_idempotency(exec_date)
        
        prefix = f"{exec_date}/archivos/"
        bucket = self.storage_client.bucket(BUCKET_NAME)
        blobs = bucket.list_blobs(prefix=prefix)
        
        rows_to_insert = []
        failed_files = [] # (DT-3) Dead Letter Queue / Exception tracking
        count = 0
        
        for blob in blobs:
            if not blob.name.split('/')[-1]:
                continue
                
            try:
                row = self.process_file(blob)
                rows_to_insert.append(row)
                count += 1
            except Exception as e:
                error_trace = traceback.format_exc()
                print(f"Error processing {blob.name}: {e}")
                failed_files.append({"file": blob.name, "error": str(e)})
                
        # (DT-3) Fail-fast / DLQ logic
        if failed_files:
            print(f"WARNING: {len(failed_files)} files failed to process.")
        
        if rows_to_insert:
            errors = self.bq_client.insert_rows_json(self.table_ref, rows_to_insert)
            if errors:
                failed_files.append({"file": "BQ_INSERT", "error": str(errors)})
                
        if failed_files:
            return {"status": "error", "failed_files": failed_files, "processed_count": count}, 500
            
        return {"status": "success", "message": f"Processed {count} files for date {exec_date}"}, 200

# Global instance for reuse
extractor = BronzeExtractor()

@functions_framework.http
def extract_to_bronze(request):
    """HTTP Cloud Function entrypoint."""
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'execution_date' in request_json:
        exec_date = request_json['execution_date']
    elif request_args and 'execution_date' in request_args:
        exec_date = request_args['execution_date']
    else:
        exec_date = datetime.utcnow().strftime('%Y/%m/%d')
        
    response_payload, status_code = extractor.run(exec_date)
    return response_payload, status_code
