terraform {
  required_version = ">= 1.6"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 6.0, < 8.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" { type = string }
variable "runtime_service_account" { type = string }
variable "region" {
  type    = string
  default = "us-central1"
}
variable "instance_name" {
  type    = string
  default = "titulacion-postgres"
}
variable "tier" {
  type    = string
  default = "db-f1-micro"
}

resource "google_project_service" "sqladmin" {
  service            = "sqladmin.googleapis.com"
  disable_on_destroy = false
}

# Solo preparar/planificar. Aplicar crea recursos facturables.
resource "google_sql_database_instance" "rag" {
  name                = var.instance_name
  region              = var.region
  database_version    = "POSTGRES_17"
  deletion_protection = true
  depends_on          = [google_project_service.sqladmin]

  settings {
    tier              = var.tier
    edition           = "ENTERPRISE"
    availability_type = "ZONAL"
    disk_type         = "PD_SSD"
    disk_size         = 10
    disk_autoresize   = false

    ip_configuration {
      ipv4_enabled = true
      ssl_mode     = "ENCRYPTED_ONLY"
      # Sin redes autorizadas: acceso previsto mediante conector Cloud SQL.
    }
    backup_configuration {
      enabled                        = true
      start_time                     = "08:00"
      point_in_time_recovery_enabled = false
      backup_retention_settings {
        retained_backups = 7
        retention_unit   = "COUNT"
      }
    }
  }
  lifecycle {
    prevent_destroy = true
  }
}

resource "google_sql_database" "rag" {
  name     = "titulacion"
  instance = google_sql_database_instance.rag.name
}

resource "google_project_iam_member" "runtime_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${var.runtime_service_account}"
}

output "instance_connection_name" {
  value = google_sql_database_instance.rag.connection_name
}

# Contraseña, usuario SQL y contenido del secreto se crean fuera de Terraform.
# Evita poner credenciales en configuración, tfvars, plan o estado de este módulo.
