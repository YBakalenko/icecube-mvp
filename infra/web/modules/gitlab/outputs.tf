output "gitlab_root_password" {
  value = data.kubernetes_secret_v1.gitlab_root_password.data.password
  sensitive = true
  description = "Gitlab root account password"
}

output "gitlab_host" {
  value = "gitlab.${var.gitlab_domain}"
  description = "Gitlab hostname"
}

output "gitlab_ip" {
  value = data.kubernetes_service_v1.gitlab_ip.status.0.load_balancer.0.ingress.0.ip
  description = "Gitlab external IP address"
}
