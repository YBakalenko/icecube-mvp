variable zone {
  description = "Default allocation region"
  default     = "ru-central1-a"
  type        = string
}

variable folder_id {
  description = "Yandex Cloud folder ID"
  default     = "ru-central1-a"
  type        = string
}

variable network_id {
  description = "Yandex Cloud network ID"
  type        = string
}

variable subnet_id {
  description = "Yandex Cloud subnet ID"
  type        = string
}

variable sa_id {
  description = "Kubernetes dedicated service account ID"
  type        = string
}

variable ssh_key_path {
  description = "SSH access key for Kubernetes nodes"
  default     = "~/.ssh/ubuntu.pub"
  type        = string
}