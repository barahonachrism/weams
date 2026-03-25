data "google_project" "project" {}

resource "google_project_service" "composer_api" {
  project = var.project_id
  service = "composer.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_iam_member" "composer_agent_ext" {
  project = var.project_id
  role    = "roles/composer.ServiceAgentV2Ext"
  member  = "serviceAccount:service-${data.google_project.project.number}@cloudcomposer-accounts.iam.gserviceaccount.com"
  depends_on = [google_project_service.composer_api]
}

resource "google_composer_environment" "composer_env" {
  name   = "weams-composer"
  region = var.region

  config {
    software_config {
      image_version = "composer-2-airflow-2"
    }
    node_config {
      service_account = google_service_account.composer_sa.email
    }
  }

  depends_on = [
    google_project_iam_member.composer_worker,
    google_project_iam_member.composer_sa_user,
    google_project_service.composer_api,
    google_project_iam_member.composer_agent_ext
  ]
}
