resource "google_storage_bucket" "landing_zone" {
  name                        = "${var.project_id}-landing"
  location                    = var.multiregion
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  force_destroy               = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}
