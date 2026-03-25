# Service Account for Cloud Function/Extractor
resource "google_service_account" "extractor_sa" {
  account_id   = "sa-bronze-extractor"
  display_name = "Service Account for Bronze Extractor (Cloud Function)"
}

# Roles for Extractor Service Account
resource "google_project_iam_member" "extractor_storage_object_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.extractor_sa.email}"
}

resource "google_project_iam_member" "extractor_bq_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.extractor_sa.email}"
}

# Service Account for Orchestration/Dataflow (Composer/Airflow)
resource "google_service_account" "orchestrator_sa" {
  account_id   = "sa-data-orchestrator"
  display_name = "Service Account for Data Pipeline Orchestrator"
}

# Roles for Orchestrator Service Account
resource "google_project_iam_member" "orchestrator_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.orchestrator_sa.email}"
}

resource "google_project_iam_member" "orchestrator_bq_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.orchestrator_sa.email}"
}

resource "google_project_iam_member" "orchestrator_dataflow_worker" {
  project = var.project_id
  role    = "roles/dataflow.worker"
  member  = "serviceAccount:${google_service_account.orchestrator_sa.email}"
}

# Service Account for Composer
resource "google_service_account" "composer_sa" {
  account_id   = "sa-composer"
  display_name = "Service Account for Cloud Composer Environment"
}

resource "google_project_iam_member" "composer_worker" {
  project = var.project_id
  role    = "roles/composer.worker"
  member  = "serviceAccount:${google_service_account.composer_sa.email}"
}

resource "google_project_iam_member" "composer_sa_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.composer_sa.email}"
}

# Service Account for Dataflow
resource "google_service_account" "dataflow_sa" {
  account_id   = "sa-dataflow"
  display_name = "Service Account for Dataflow Pipelines"
}

resource "google_project_iam_member" "dataflow_worker" {
  project = var.project_id
  role    = "roles/dataflow.worker"
  member  = "serviceAccount:${google_service_account.dataflow_sa.email}"
}

resource "google_project_iam_member" "dataflow_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.dataflow_sa.email}"
}

resource "google_project_iam_member" "dataflow_bq_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.dataflow_sa.email}"
}

# Service Account for Looker Studio / BI
resource "google_service_account" "looker_sa" {
  account_id   = "sa-looker"
  display_name = "Service Account for Looker Studio Dashboards"
}

# Role to allow executing queries in the GCP Project
resource "google_project_iam_member" "looker_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.looker_sa.email}"
}

# Role to allow reading data but restricted ONLY to the Gold dataset
resource "google_bigquery_dataset_iam_member" "looker_data_viewer_gold" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.gold.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.looker_sa.email}"
}
