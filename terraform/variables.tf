locals {
  data_lake_bucket = "mtg_data_lake"
}

variable "project" {
  description = "Your GCP project ID" 
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default = "europe-west6"
  type = string
}

variable "storage_class" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default = "STANDARD"
}

variable "bq_dataset" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type = string
  default = "mtg_card_data_raw"
}

variable "dbt_dataset" {
  description = "DBT dataset that will feed into the visualization layer"
  type = string
  default = "mtg_card_data_dbt"
}