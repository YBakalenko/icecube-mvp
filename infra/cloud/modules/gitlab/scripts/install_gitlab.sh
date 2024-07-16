#!/bin/bash
set -e

GITLAB_DOMAIN=$1

helm repo add gitlab https://charts.gitlab.io/ --force-update

helm upgrade --install gitlab gitlab/gitlab \
    --set global.edition=ce \
    --set global.hosts.domain=${GITLAB_DOMAIN} \
    --set global.ingress.configureCertmanager=false \
    --set certmanager.install=false \
    --set gitlab-runner.install=false

kubectl get secret gitlab-gitlab-initial-root-password -ojsonpath='{.data.password}' | base64 --decode ; echo
