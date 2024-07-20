variable "gitlab_ip" {
  description = "GitLab IP address"
  type        = string
}

variable "gitlab_host" {
  description = "GitLab hostname"
  type        = string
  default     = "gitlab.example.com"
}

variable "runners_token" {
  description = "GitLab runner token to register"
  type        = string
  sensitive   = true
}
