provider "yandex" {
  service_account_key_file = var.sa_key_file
  cloud_id                 = var.cloud_id
  folder_id                = var.folder_id
  zone                     = var.zone
}

module "vpc" {
  source          = "./modules/vpc"
  zone            = var.zone
}

module "k8s" {
  source          = "./modules/k8s"
  zone            = var.zone
  folder_id       = var.folder_id
  network_id      = module.vpc.vpc_network_id
  subnet_id       = module.vpc.vpc_subnet_id
  sa_id           = var.sa_id
  ssh_key_path    = var.ssh_key_path
}
