# These roles will be required for Gitlab runner to create, modify, delete namespaces, pods etc:
resource "kubernetes_cluster_role_v1" "namespace_admin" {
  metadata {
    name = "namespace-admin"
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "namespaces", "resourcequotas", "limitranges", "secrets", "persistentvolumes", "persistentvolumeclaims", "services", "serviceaccounts", "configmaps"]
    verbs      = ["get", "create", "list", "watch", "delete", "update"]
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
  rule {
    api_groups = ["policy"]
    resources  = ["poddisruptionbudgets"]
    verbs      = ["get", "create", "list", "watch", "delete", "update"]
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
    namespace = "gitlab"
    api_group = ""
  }
}
