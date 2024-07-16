variable "gitlab_domain" {
  description = "GitLab instance domain name"
  default     = "example.com"
  type        = string
}

variable "gitlab_ip" {
  description = "GitLab instance external IP"
  type        = string
}

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
