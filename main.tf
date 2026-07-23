terraform {
  required_version = ">= 1.0.0"
  backend "gcs" {
    bucket = "hackathondb2026-cloudrun-app-tfstate-bucket"
    prefix = "app/state"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# --- D & G. CLOUD RUN SERVICE ---
resource "google_cloud_run_v2_service" "app_service" {
  name                = "cloudrun-app-server"
  location            = var.region
  ingress             = "INGRESS_TRAFFIC_ALL"
  deletion_protection = false 

  template {
    service_account = var.cloudrun_sa_email
    encryption_key  = var.kms_key_id
    
    containers {
      image = "${var.registry_url}/my-app:${var.image_tag}"
      
      ports {
        container_port = 8080
      }

      # Mount the secret volume as a physical file inside the container
      volume_mounts {
        name       = "env-volume"
        mount_path = "/app/secrets"
      }
    }

    # Reference the secret container asset
    volumes {
      name = "env-volume"
      secret {
        secret = "app-env-config"
        items {
          version = "latest"
          path    = ".env" # Saves it as /app/secrets/.env
        }
      }
    }

    # FIXED: Nested properly inside the template block
    vpc_access {
      connector = var.vpc_connector_id
      #egress    = "ALL_TRAFFIC"
      egress     = "PRIVATE_RANGES_ONLY" 
    }
  } # Closes template block
} # Closes google_cloud_run_v2_service block

# Public Access binding
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.app_service.name
  location = google_cloud_run_v2_service.app_service.location
  member   = "allUsers"
  role     = "roles/run.invoker" 
}
