provider "kubernetes" {
  config_path = "~/.kube/config" # Path to your kubeconfig file
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config" # Path to your kubeconfig file
  }
}

module "nginx" {
  source = "./modules/nginx"
}

module "gitlab" {
  source        = "./modules/gitlab"
  depends_on    = [module.nginx]
  gitlab_domain = var.enterprise_domain
}

module "prometheus" {
  source            = "./modules/prometheus"
  depends_on        = [module.gitlab]
  prometheus_host   = "prometheus.${var.enterprise_domain}"
  alertmanager_host = "alertmanager.${var.enterprise_domain}"
  grafana_host      = "grafana.${var.enterprise_domain}"
}
