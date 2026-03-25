import argparse
import ast
import json
import logging
from datetime import datetime

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class ParseAndNormalize(beam.DoFn):
    def process(self, element, execution_date, taxonomy_dict):
        """
        Parses the extracted_content from row.
        Normalizes skills based on taxonomy.
        Yields normalized rows or tags as DLQ.
        """
        try:
            content_str = element.get('extracted_content', '{}')
            
            try:
                data = json.loads(content_str)
            except:
                data = {"raw_text": str(content_str)}
                
            raw_text = str(data).lower()
            
            found_skills = []
            for key, standardized_name in taxonomy_dict.items():
                if key in raw_text:
                    found_skills.append(standardized_name)
                    
            seniority = "Junior"
            if "senior" in raw_text or "experiencia: 5" in raw_text or "experiencia: 4" in raw_text:
                seniority = "Senior"
            elif "arquitect" in raw_text or "architect" in raw_text:
                seniority = "Arquitecto"
                
            if not found_skills:
                yield beam.pvalue.TaggedOutput('dlq', {
                    "file_name": element.get('file_name'),
                    "error_reason": "No relevant Java skills detected",
                    "execution_date": execution_date
                })
                return

            for skill in found_skills:
                yield {
                    "file_name": element.get('file_name'),
                    "skill_name": skill,
                    "seniority_level": seniority,
                    "execution_date": execution_date,
                    "processed_timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logging.error(f"Error processing row: {e}")
            yield beam.pvalue.TaggedOutput('dlq', {
                "file_name": element.get('file_name', 'UNKNOWN'),
                "error_reason": str(e),
                "execution_date": execution_date
            })

def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_id', required=True, help='GCP Project ID')
    parser.add_argument('--execution_date', required=True, help='Logical execution date (YYYY-MM-DD)')
    parser.add_argument('--bronze_table', required=True, help='Bronze BigQuery table to read from e.g. bronze.raw_transcriptions')
    parser.add_argument('--silver_table', required=True, help='Silver BigQuery table to write to e.g. silver.normalized_skills')
    parser.add_argument('--dlq_table', required=True, help='Silver DLQ BigQuery table to write to e.g. silver.normalized_skills_dlq')
    parser.add_argument('--taxonomy_table', required=True, help='Silver BigQuery table to read taxonomy from')
    
    known_args, pipeline_args = parser.parse_known_args(argv)
    
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True
    
    read_query = f"""
        SELECT file_name, extracted_content 
        FROM `{known_args.project_id}.{known_args.bronze_table}`
        WHERE DATE(ingestion_timestamp) = '{known_args.execution_date}'
          OR file_path LIKE '%{known_args.execution_date.replace("-", "/")}%'
    """
    
    taxonomy_query = f"""
        SELECT keyword, standardized_name 
        FROM `{known_args.project_id}.{known_args.taxonomy_table}`
    """

    with beam.Pipeline(options=pipeline_options) as p:
        
        # 0. Read Taxonomy Side Input
        taxonomies = (
            p 
            | 'ReadTaxonomy' >> beam.io.ReadFromBigQuery(query=taxonomy_query, use_standard_sql=True, project=known_args.project_id)
            | 'FormatTaxonomy' >> beam.Map(lambda row: (str(row['keyword']).lower(), str(row['standardized_name'])))
        )
        
        # 1. Read from Bronze
        bronze_rows = (
            p 
            | 'ReadFromBronze' >> beam.io.ReadFromBigQuery(query=read_query, use_standard_sql=True, project=known_args.project_id)
        )
        
        # 2. Process and Split (Main vs DLQ) using Side Input
        processed = (
            bronze_rows 
            | 'NormalizeSkills' >> beam.ParDo(ParseAndNormalize(), known_args.execution_date, beam.pvalue.AsDict(taxonomies)).with_outputs('dlq', main='main')
        )
        
        silver_schema = {
            'fields': [
                {'name': 'file_name', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'skill_name', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'seniority_level', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'execution_date', 'type': 'DATE', 'mode': 'REQUIRED'},
                {'name': 'processed_timestamp', 'type': 'TIMESTAMP', 'mode': 'REQUIRED'},
            ]
        }
        
        dlq_schema = {
            'fields': [
                {'name': 'file_name', 'type': 'STRING', 'mode': 'NULLABLE'},
                {'name': 'error_reason', 'type': 'STRING', 'mode': 'NULLABLE'},
                {'name': 'execution_date', 'type': 'DATE', 'mode': 'REQUIRED'},
            ]
        }

        # 3. Write Main to Silver
        _ = (
            processed.main
            | 'WriteToSilver' >> beam.io.WriteToBigQuery(
                f"{known_args.project_id}:{known_args.silver_table}",
                schema=silver_schema,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
            )
        )
        
        # 4. Write DLQ
        _ = (
            processed.dlq
            | 'WriteToDLQ' >> beam.io.WriteToBigQuery(
                f"{known_args.project_id}:{known_args.dlq_table}",
                schema=dlq_schema,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
            )
        )

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
