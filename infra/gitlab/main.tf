provider "helm" {
  kubernetes {
    config_path    = "~/.kube/config"  # Path to your kubeconfig file
  }
}

provider "kubernetes" {
  config_path    = "~/.kube/config"
}

# These roles will be required for Gitlab runner to create, modify, delete namespaces, pods etc:
resource "kubernetes_cluster_role_v1" "namespace_admin" {
  metadata {
    name = "namespace-admin"
  }

  rule {
    api_groups = [""]
    resources  = ["namespaces", "resourcequotas", "limitranges", "secrets", "persistentvolumes", "persistentvolumeclaims", "services"]
    verbs      = ["get", "create", "list", "watch", "delete"]
  }
  rule {
    api_groups = ["networking.k8s.io"]
    resources  = ["networkpolicies", "ingresses"]
    verbs      = ["get", "create", "list", "watch"]
  }
  rule {
    api_groups = ["apps"]
    resources  = ["deployments", "replicasets"]
    verbs      = ["get", "create", "list", "watch"]
  }
}

resource "kubernetes_cluster_role_binding_v1" "namespace_admin_binding" {
  depends_on = [kubernetes_cluster_role_v1.namespace_admin]
  metadata {
    name = "namespace-admin-binding"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "namespace-admin"
  }
  subject {
    kind      = "ServiceAccount"
    name      = "default"
    api_group = ""
  }
}

data "kubernetes_service_v1" "gitlab_ip" {
  metadata {
    name      = "gitlab-nginx-ingress-controller"
    namespace = "gitlab"
  }
}

data "kubernetes_ingress_v1" "gitlab_host" {
  metadata {
    name      = "gitlab-webservice-default"
    namespace = "gitlab"
  }
}

locals {
  runner_values_yaml_content           = templatefile("${path.module}/files/values.yaml.tpl", {
    gitlab_host                        = data.kubernetes_ingress_v1.gitlab_host.spec.0.tls.0.hosts.0
    gitlab_ip                          = data.kubernetes_service_v1.gitlab_ip.status.0.load_balancer.0.ingress.0.ip
    runner_token                       = var.runner_token
  })
}

resource "helm_release" "gitlab_runner" {
  name       = "gitlab-runner"
  repository = "https://charts.gitlab.io"
  chart      = "gitlab-runner"
  version    = "0.66.0"
  namespace  = "gitlab"

  values = [local.runner_values_yaml_content]
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

resource "helm_release" "kube-agent" {
  name             = "kube-agent"
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
    value = "${var.agent_token}"
  }
  set {
    name  = "config.kasAddress"
    value = "wss://${data.kubernetes_ingress_v1.kas_host.spec.0.tls.0.hosts.0}"
  }
  set {
    name  = "config.kasCaCert"
    value = "${data.kubernetes_secret_v1.gitlab_ca_cert.data.cfssl_ca}"
  }
  set {
    name  = "hostAliases[0].ip"
    value = "${data.kubernetes_service_v1.gitlab_ip.status.0.load_balancer.0.ingress.0.ip}"
  }
  set {
    name  = "hostAliases[0].hostnames[0]"
    value = "${data.kubernetes_ingress_v1.kas_host.spec.0.tls.0.hosts.0}"
  }

}
