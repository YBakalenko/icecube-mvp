1. Create a Yandex Cloud infrastructure: deploy Kubernetes
```
cd cloud
terraform init
terraform apply
```
2. Deploy NGINX Ingress Controller and Gitlab:
```
cd ../web
terraform init
terraform apply
```
3. Update `/etc/hosts` file with Gitlab IP and hostname `gitlab.example.com`
4. To printout Gitlab `root` account password use command:
```
terraform output -raw gitlab_root_password
```
5. Login to Gitlab server [https://gitlab.example.com](https://gitlab.example.com)
- Create a Gitlab runner (`Admin Area > CI/CD > Runners > New instance runner`) and paste its token to `gitlab/terraform.tfvars` file
- Create your group and project
- In your project create a Kubernetes agent (`Project > Operate > Kubernetes clusters > Connect a cluster`) and paste its token to `gitlab/terraform.tfvars` file
- Update `gitlab_ip` value to math Terraform outputs
6. Install and register Gitlab runner and Kubernetes agent
```
cd ../gitlab
terraform init
terraform apply
```
