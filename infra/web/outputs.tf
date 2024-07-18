output "ingress_ip" {
  value = module.nginx.ingress_ip
}

output "gitlab_root_password" {
  value = module.gitlab.gitlab_root_password
  sensitive = true
}

output "gitlab_ip" {
  value = module.gitlab.gitlab_ip
}
