output "ingress_ip" {
  value       = module.nginx.ingress_ip
  description = "Ingress external IP for applications"
}

output "gitlab_root_password" {
  value       = module.gitlab.gitlab_root_password
  sensitive   = true
  description = "Gitlab root account password"
}

output "gitlab_ip" {
  value       = module.gitlab.gitlab_ip
  description = "Gitlab server external IP"
}

output "prometheus_host" {
  value       = "prometheus.${var.enterprise_domain}"
  description = "Prometheus server hostname"
}

output "alertmanager_host" {
  value       = "alertmanager.${var.enterprise_domain}"
  description = "Alertmanager server hostname"
}

output "grafana_host" {
  value       = "grafana.${var.enterprise_domain}"
  description = "Grafana server hostname"
}
