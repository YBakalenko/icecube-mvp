resource "gitlab_cluster_agent" "agent" {
  project    = "${var.project_id}"
  name       = "${var.project_name}-agent"
}

resource "gitlab_cluster_agent_token" "token" {
  project = gitlab_cluster_agent.agent.project
  agent_id    = gitlab_cluster_agent.agent.agent_id
  name     = "${var.project_name}-agent-token"
  description = "${var.project_name} Kubernetes agent token"
}

data "kubernetes_ingress_v1" "kas_host" {
  metadata {
    name      = "gitlab-kas"
    namespace = "gitlab"
  }
}

data "kubernetes_secret_v1" "gitlab_ca_cert" {
  metadata {
    name      = "gitlab-wildcard-tls-ca"
    namespace = "gitlab"
  }
}

data "kubernetes_service_v1" "gitlab_ip" {
  metadata {
    name      = "gitlab-nginx-ingress-controller"
    namespace = "gitlab"
  }
}

resource "helm_release" "kube-agent" {
  name             = "kube-agent-${var.project_name}"
  repository       = "https://charts.gitlab.io/"
  chart            = "gitlab-agent"
  version          = "2.4.0"
  namespace        = "gitlab-agent-kube-agent"
  create_namespace = "true"

  set {
    name  = "image.tag"
    value = "v17.1.2"
  }
  set {
    name  = "config.token"
    value = gitlab_cluster_agent_token.token.token
  }
  set {
    name  = "config.kasAddress"
    value = "wss://${data.kubernetes_ingress_v1.kas_host.spec[0].tls[0].hosts[0]}"
  }
  set {
    name  = "config.kasCaCert"
    value = data.kubernetes_secret_v1.gitlab_ca_cert.data.cfssl_ca
  }
  set {
    name  = "hostAliases[0].ip"
    value = data.kubernetes_service_v1.gitlab_ip.status[0].load_balancer[0].ingress[0].ip
  }
  set {
    name  = "hostAliases[0].hostnames[0]"
    value = data.kubernetes_ingress_v1.kas_host.spec[0].tls[0].hosts[0]
  }
}
