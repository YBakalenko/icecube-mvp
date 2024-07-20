variable prometheus_host {
  description = "Prometheus Ingress hostname"
  type        = string
  default     = "prometheus.example.com"
}

variable alertmanager_host {
  description = "Alertmanager Ingress hostname"
  type        = string
  default     = "alertmanager.example.com"
}

variable grafana_host {
  description = "Grafana Ingress hostname"
  type        = string
  default     = "grafana.example.com"
}
