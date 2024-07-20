resource "helm_release" "prometheus" {
  name              = "prometheus"
  chart             = "../../deploy/prometheus"
  version           = "0.1.0"
  namespace         = "default"
  dependency_update = "true"
  create_namespace  = "true"
  wait              = "true"
  wait_for_jobs     = "true"


  set {
    name  = "kube-prometheus-stack.prometheus.ingress.hosts[0]"
    value = "${var.prometheus_host}"
  }
  set {
    name  = "kube-prometheus-stack.alertmanager.ingress.hosts[0]"
    value = "${var.alertmanager_host}"
  }
  set {
    name  = "kube-prometheus-stack.grafana.ingress.hosts[0]"
    value = "${var.grafana_host}"
  }
}
