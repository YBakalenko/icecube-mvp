resource "gitlab_runner" "basic_runner" {
  registration_token = var.runners_token
  run_untagged = "true"
}

locals {
  runner_values_yaml_content = templatefile("${path.module}/files/values.yaml", {
    gitlab_host  = var.gitlab_host
    gitlab_ip    = var.gitlab_ip
    runner_token = "${gitlab_runner.basic_runner.authentication_token}"
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
