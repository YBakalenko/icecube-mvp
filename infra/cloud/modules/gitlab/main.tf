resource "terraform_data" "install_gitlab" {
  provisioner "local-exec" {
    command = "bash ${path.module}/scripts/install_gitlab.sh ${var.gitlab_domain}"
  }
}

resource "time_sleep" "wait_300_seconds" {
  # Wait for 5 minutes to make gitlab webservice obtain an external IP address
  depends_on = [terraform_data.install_gitlab]

  create_duration = "300s"
}

resource "terraform_data" "update_hosts" {
  depends_on = [time_sleep.wait_300_seconds]
  provisioner "local-exec" {
    command = "bash ${path.module}/scripts/update_hosts.sh ${var.gitlab_domain}"
  }
}
