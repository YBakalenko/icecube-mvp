resource "terraform_data" "ingress-nginx" {
  provisioner "local-exec" {
    command = "kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml"
  }
}

# Wait for 30 sec to obtain LoadBalancer IP
resource "time_sleep" "nginx_lb_wait" {
  depends_on = [terraform_data.ingress-nginx]

  create_duration = "30s"
}

data "kubernetes_service_v1" "nginx_ingress" {
  depends_on  = [time_sleep.nginx_lb_wait]
  metadata {
    name      = "ingress-nginx-controller"
    namespace = "ingress-nginx"
  }
}
