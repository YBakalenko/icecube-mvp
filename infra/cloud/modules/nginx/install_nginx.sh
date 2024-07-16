#!/bin/bash
set -e


# kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
# helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx --force
# helm repo update
# helm install ingress-nginx ingress-nginx/ingress-nginx

helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx
