provider "helm" {
  kubernetes {
    config_path    = "~/.kube/config"  # Path to your kubeconfig file
  }
}

locals {
  runner_values_yaml_content           = templatefile("${path.module}/files/values.yaml.tpl", {
    gitlab_domain                      = var.gitlab_domain
    gitlab_ip                          = var.gitlab_ip
    runner_token                       = var.runner_token
  })
}

resource "helm_release" "gitlab_runner" {
  name       = "gitlab-runner"
  repository = "https://charts.gitlab.io"
  chart      = "gitlab-runner"
  version    = "0.66.0"
  namespace  = "default"

  values = [local.runner_values_yaml_content]
}

resource "terraform_data" "install_agent" {
  depends_on = [helm_release.gitlab_runner]
  provisioner "local-exec" {
    command = "bash ${path.module}/files/install_agent.sh  ${var.gitlab_domain}  ${var.gitlab_ip}  ${var.agent_token}"
  }
}
