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
- Create a Personal Access Token (`User Settings > Access Tokens`) and paste its token to `gitlab/terraform.tfvars` file
6. Create a group, projects, group variables, install and register Gitlab runner and Kubernetes agents
```
cd ../gitlab
terraform init
terraform apply
```
Enter your Dockerhub username and password when prompted
