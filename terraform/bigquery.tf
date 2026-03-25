resource "google_bigquery_dataset" "bronze" {
  dataset_id                  = "bronze"
  friendly_name               = "Bronze Dataset"
  description                 = "Dataset for raw unstructured data transcription (JSON)"
  location                    = var.multiregion
  delete_contents_on_destroy  = true
}

resource "google_bigquery_table" "bronze_transcriptions" {
  dataset_id = google_bigquery_dataset.bronze.dataset_id
  table_id   = "raw_transcriptions"
  deletion_protection = false

  schema = <<EOF
[
  {
    "name": "file_name",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Name of the original file"
  },
  {
    "name": "file_path",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "GCS path to the original file"
  },
  {
    "name": "extracted_content",
    "type": "JSON",
    "mode": "NULLABLE",
    "description": "JSON structured content extracted from the file"
  },
  {
    "name": "ingestion_timestamp",
    "type": "TIMESTAMP",
    "mode": "REQUIRED",
    "description": "Timestamp when the file was processed"
  }
]
EOF
}

resource "google_bigquery_dataset" "silver" {
  dataset_id                  = "silver"
  friendly_name               = "Silver Dataset"
  description                 = "Dataset for structured, cleaned, and normalized data"
  location                    = var.multiregion
  delete_contents_on_destroy  = false
}

resource "google_bigquery_dataset" "gold" {
  dataset_id                  = "gold"
  friendly_name               = "Gold Dataset"
  description                 = "Dataset for analytics, reporting, and dimensional models"
  location                    = var.multiregion
  delete_contents_on_destroy  = false
}
