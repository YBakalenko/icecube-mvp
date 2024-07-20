provider "helm" {
  kubernetes {
    config_path = "~/.kube/config" # Path to your kubeconfig file
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
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

# These roles will be required for Gitlab runner to create, modify, delete namespaces, pods etc:
module "roles" {
  source = "./modules/roles"
}

provider "gitlab" {
  base_url = "https://${data.kubernetes_ingress_v1.gitlab_host.spec[0].tls[0].hosts[0]}/"
  # https://gitlab.example.com/
  token    = var.gitlab_token
  insecure = "true"
}

resource "gitlab_group" "my_group" {
  name             = var.username
  path             = var.username
  description      = "My CI/CD group"
  visibility_level = "public"
}

module "runner" {
  gitlab_ip     = data.kubernetes_service_v1.gitlab_ip.status[0].load_balancer[0].ingress[0].ip
  gitlab_host   = data.kubernetes_ingress_v1.gitlab_host.spec[0].tls[0].hosts[0]
  runners_token = gitlab_group.my_group.runners_token
  source        = "./modules/runner"
}

resource "gitlab_project" "projects" {
  for_each         = toset(var.project_names)
  name             = each.key
  visibility_level = "public"
  description      = "${each.key} CI/CD project"
  namespace_id     = gitlab_group.my_group.id
}

module "kas_agents" {
  for_each     = gitlab_project.projects
  project_id   = gitlab_project.projects[each.key].id # "${each.key}"
  project_name = gitlab_project.projects[each.key].name # "${each.key}"
  source       = "./modules/agent"
}

resource "gitlab_group_variable" "ci_registry_user" {
  depends_on        = [gitlab_group.my_group]
  group             = var.username
  key               = "CI_REGISTRY_USER"
  value             = var.username
  protected         = false
  masked            = false
  environment_scope = "*"
}

resource "gitlab_group_variable" "ci_registry_password" {
  depends_on        = [gitlab_group.my_group]
  group             = var.username
  key               = "CI_REGISTRY_PASSWORD"
  value             = var.password
  protected         = true
  masked            = false
  environment_scope = "*"
}

resource "gitlab_group_variable" "ci_gitlab_ip" {
  depends_on        = [gitlab_group.my_group]
  group             = var.username
  key               = "CI_GITLAB_IP"
  value             = data.kubernetes_service_v1.gitlab_ip.status[0].load_balancer[0].ingress[0].ip
  protected         = false
  masked            = false
  environment_scope = "*"
}

resource "gitlab_group_variable" "ci_gitlab_host" {
  depends_on        = [gitlab_group.my_group]
  group             = var.username
  key               = "CI_GITLAB_HOST"
  value             = data.kubernetes_ingress_v1.gitlab_host.spec[0].tls[0].hosts[0]
  protected         = false
  masked            = false
  environment_scope = "*"
}
