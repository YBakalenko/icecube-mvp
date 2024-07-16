output "vpc_network_id" {
  value = yandex_vpc_network.k8s-network.id
}

output "vpc_subnet_id" {
  value = yandex_vpc_subnet.k8s-subnet.id
}
