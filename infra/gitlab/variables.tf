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

# variable "runner_token" {
#   description = "GitLab runner token to register"
#   type        = string
#   sensitive   = true
# }

# variable "frontend_kas_token" {
#   description = "GitLab Kubernetes agent token to register for frontend project"
#   type        = string
#   sensitive   = true
# }

# variable "train_kas_token" {
#   description = "GitLab Kubernetes agent token to register for train project"
#   type        = string
#   sensitive   = true
# }

# variable "predict_kas_token" {
#   description = "GitLab Kubernetes agent token to register for predict project"
#   type        = string
#   sensitive   = true
# }

# variable "deploy_kas_token" {
#   description = "GitLab Kubernetes agent token to register for frontend project"
#   type        = string
#   sensitive   = true
# }
