variable "sa_key_file" {
  description = "Service account JSON key file path"
  type        = string
}

variable "sa_id" {
  description = "Service account ID"
  type        = string
}

variable "cloud_id" {
  description = "Yandex Cloud ID"
  type        = string
}

variable "folder_id" {
  description = "Yandex Cloud Folder ID (default)"
  type        = string
}

variable "zone" {
  description = "Yandex Cloud zone name"
  default     = "ru-central1"
  type        = string
}

variable "ssh_key_path" {
  description = "SSH key file path for k8s access"
  type        = string
}
