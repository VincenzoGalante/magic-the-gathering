terraform {
  required_version = ">= 1.0"
  backend "local" {}  # Can change from "local" to "gcs" (for google) or "s3" (for aws), if you would like to preserve your tf-state online
  required_providers {
    google = {
      source  = "hashicorp/google"
    }
  }
}

provider "google" {
  project = var.project
  region = var.region
  // credentials = file(var.credentials)  # Use this if you do not want to set env-var GOOGLE_APPLICATION_CREDENTIALS
}

# Data Lake Bucket
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
resource "google_storage_bucket" "data-lake-bucket" {
  name          = "${var.project}_${local.data_lake_bucket}" # Concatenating DL bucket & Project name for unique naming
  location      = var.region

  # Optional, but recommended settings:
  storage_class = var.storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled     = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30  // days
    }
  }

  force_destroy = true
}

resource "google_bigquery_dataset" "mtg_card_data_raw" {
  dataset_id = var.bq_dataset
  project    = var.project
  location   = var.region
}

resource "google_bigquery_dataset" "mtg_card_data_dbt" {
  dataset_id = var.dbt_dataset
  project    = var.project
  location   = var.region
}

resource "google_bigquery_table" "default_cards" {
  dataset_id = google_bigquery_dataset.mtg_card_data_raw.dataset_id
  table_id   = "default_cards"

  schema = <<EOF
  [
    {
      "name": "card_id",
      "type" : "STRING",
      "mode" : "NULLABLE",
      "description": "The ID of the card in the database"
    },
    {
      "name": "name",
      "type" : "STRING",
      "mode" : "NULLABLE",
      "description": "The name of the card"
    },
    {
      "name": "released_at",
      "type" : "TIMESTAMP",
      "mode" : "NULLABLE",
      "description": "The date the card was released"
    },
    {
      "name": "color_identity",
      "type" : "STRING",
      "mode" : "NULLABLE",
      "description": "The color identity of the card"
    },
    {
      "name": "set_name",
      "type" : "STRING",
      "mode" : "NULLABLE",
      "description": "The name of the set the card is from"
    },
    {
      "name": "artist",
      "type" : "STRING",
      "mode" : "NULLABLE",
      "description": "The artist of the card"
    },
    {
      "name": "price",
      "type": "FLOAT",
      "mode": "NULLABLE",
      "description": "The price of the card in US Dollar"
    },
    {
      "name": "data_update",
      "type": "TIMESTAMP",
      "mode": "NULLABLE",
      "description": "The date the data was last updated"
    }
  ] 
  EOF
}