variable "project_id" {
  type    = string
  default = "project-495bdca4-ac50-4df5-bb6"
}
variable "region"     { 
   type = string
   default = "us-central1" 
}
variable "vpc_connector_id"     { 
   type = string
   default = "projects/project-495bdca4-ac50-4df5-bb6/locations/us-central1/connectors/cr-vpc-connector" 
}

variable "kms_key_id"     { 
   type = string
   default = "projects/project-495bdca4-ac50-4df5-bb6/locations/us-central1/keyRings/cloudrun-keyring/cryptoKeys/cloudrun-customer-key" 
}

variable "cloudrun_sa_email"     { 
   type = string
   default = "cloud-run-runtime-sa@project-495bdca4-ac50-4df5-bb6.iam.gserviceaccount.com" 
}

variable "registry_url"     { 
   type = string
   default = "us-central1-docker.pkg.dev/project-495bdca4-ac50-4df5-bb6/app-docker-images" 
}

variable "image_tag"     { 
   type = string
   default = "latest" 
}

