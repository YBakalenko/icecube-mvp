1. Create a Yandex Cloud infrastructure: deploy Kubernetes and Gitlab server
```
cd cloud
terraform init
terraform apply
```
When prompted enter your admin account password to register a Gitlab server IP address in `/etc/hosts` file
2. Copy a root password from Terraform console print and login to Gitlab server [https://gitlab.example.com](https://gitlab.example.com)
- Create a Gitlab runner (`Admin Area > CI/CD > Runners > New instance runner`) and paste its token to `gitlab/terraform.tfvars` file
- Create your group and project
- In your project create a Kubernetes agent (`Project > Operate > Kubernetes clusters > Connect a cluster`) and paste its token to `gitlab/terraform.tfvars` file
- Update `gitlab_ip` value to math Terraform outputs
3. Install and register Gitlab runner and Kubernetes agent
```
cd ../gitlab
terraform init
terraform apply
```
