resource "helm_release" "gitlab" {
  name             = "gitlab"
  repository       = "https://charts.gitlab.io/"
  chart            = "gitlab"
  version          = "8.1.2"
  namespace        = "gitlab"
  create_namespace = "true"
  wait             = "true"
  wait_for_jobs    = "true"
  timeout          = "1200"

  set {
    name  = "global.edition"
    value = "ce"
  }
  set {
    name  = "global.hosts.domain"
    value = "${var.gitlab_domain}"
  }
  set {
    name  = "global.ingress.configureCertmanager"
    value = "false"
  }
  set {
    name  = "certmanager.install"
    value = "false"
  }
  set {
    name  = "gitlab-runner.install"
    value = "false"
  }
}

data "kubernetes_secret_v1" "gitlab_root_password" {
  depends_on = [helm_release.gitlab]
  metadata {
    name      = "gitlab-gitlab-initial-root-password"
    namespace = "gitlab"
  }
}

# Wait for 60 sec to obtain LoadBalancer IP
resource "time_sleep" "gitlab_nginx_lb_wait" {
  depends_on = [helm_release.gitlab]
  create_duration = "60s"
}

data "kubernetes_service_v1" "gitlab_ip" {
  depends_on = [time_sleep.gitlab_nginx_lb_wait]
  metadata {
    name      = "gitlab-nginx-ingress-controller"
    namespace = "gitlab"
  }
}
