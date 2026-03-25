variable "project_id" {
  description = "The GCP Project ID"
  type        = string
}

variable "region" {
  description = "The default GCP region"
  type        = string
  default     = "us-central1"
}

variable "multiregion" {
  description = "The multiregion location for BigQuery and GCS"
  type        = string
  default     = "US"
}

variable "environment" {
  description = "The environment (e.g. dev, prod)"
  type        = string
  default     = "dev"
}
