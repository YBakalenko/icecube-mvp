resource "terraform_data" "install_nginx" {
  provisioner "local-exec" {
    command = "bash ${path.module}/install_nginx.sh"
  }
}