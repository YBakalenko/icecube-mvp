output "gitlab_root_password" {
  value = data.kubernetes_secret_v1.gitlab_root_password.data.password
  sensitive = true
}

output "gitlab_ip" {
  value = data.kubernetes_service_v1.gitlab_ip.status.0.load_balancer.0.ingress.0.ip
}
