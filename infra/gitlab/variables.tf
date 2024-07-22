variable "gitlab_token" {
  description = "GitLab personal access token"
  type        = string
  sensitive   = true
}

variable "username" {
  description = "Username for Docker Hub and Group name"
  type        = string
}

variable "password" {
  description = "Password for Docker Hub"
  type        = string
  sensitive   = true
}

variable "project_names" {
  description = "GitLab projects to create"
  type        = list(string)
  default     = ["frontend", "train", "predict", "deploy"]
}
