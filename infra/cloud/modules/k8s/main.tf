resource "yandex_kubernetes_cluster" "k8s-cluster" {
  name        = "k8s-cluster"
  network_id  = var.network_id

  master {
    version = "1.29"

    zonal {
      zone      = var.zone
      subnet_id = var.subnet_id
    }

    public_ip = true

    security_group_ids = []

    maintenance_policy {
      auto_upgrade = true
    }

    master_logging {
      enabled = false
      kube_apiserver_enabled = false
      cluster_autoscaler_enabled = false
      events_enabled = false
      audit_enabled = false
    }
  }

  service_account_id      = var.sa_id
  node_service_account_id = var.sa_id

  release_channel = "RAPID"
}

resource "yandex_kubernetes_node_group" "node-group" {
  cluster_id  = yandex_kubernetes_cluster.k8s-cluster.id
  name        = "k8s-nodes"
  version     = "1.29"

  instance_template {
    name = "k8s-node-{instance.short_id}-{instance_group.id}"
    platform_id = "standard-v3"
    network_acceleration_type = "standard"
    container_runtime {
      type = "containerd"
    }

    resources {
      memory = 8
      cores  = 4
      core_fraction = 50
    }

    boot_disk {
      size = 96
    }

    network_interface {
      subnet_ids = [var.subnet_id]
      nat        = true
    }

    scheduling_policy {
      preemptible = true
    }

    metadata = {
      ssh-keys = "ubuntu:${file(var.ssh_key_path)}"
    }
  }

  scale_policy {
    fixed_scale {
      size = 2
    }
  }

  deploy_policy {
    max_unavailable = 1
    max_expansion   = 3
  }
}

resource "terraform_data" "export_kubeconfig" {
  depends_on = [yandex_kubernetes_node_group.node-group]
  provisioner "local-exec" {
    command = "yc managed-kubernetes cluster get-credentials k8s-cluster --external --force"
  }
}
