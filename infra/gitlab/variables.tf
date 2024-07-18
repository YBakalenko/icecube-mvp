variable "runner_token" {
  description = "GitLab runner token to register"
  type        = string
  sensitive   = true
}

variable "agent_token" {
  description = "GitLab Kubernetes agent token to register"
  type        = string
  sensitive   = true
}
