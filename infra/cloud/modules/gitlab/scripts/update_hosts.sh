#!/bin/bash
set -e

GITLAB_DOMAIN=$1

GITLAB_IP=$(kubectl get svc --namespace default gitlab-nginx-ingress-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "${GITLAB_IP} gitlab.${GITLAB_DOMAIN}" | sudo tee -a /etc/hosts

kubectl get ingress -lrelease=gitlab
