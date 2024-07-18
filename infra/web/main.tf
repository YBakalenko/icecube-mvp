provider "kubernetes" {
  config_path    = "~/.kube/config"  # Path to your kubeconfig file
}

provider "helm" {
  kubernetes {
    config_path    = "~/.kube/config"  # Path to your kubeconfig file
  }
}

module "nginx" {
  source          = "./modules/nginx"
}

module "gitlab" {
  source          = "./modules/gitlab"
  depends_on      = [module.nginx]
  gitlab_domain   = var.gitlab_domain
}
