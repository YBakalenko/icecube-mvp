#!/bin/bash
set -e

GITLAB_DOMAIN=$1
GITLAB_IP=$2
AGENT_TOKEN=$3

kubectl apply -f ./files/namespace-admin-role.yaml
kubectl apply -f ./files/namespace-admin-binding.yaml

kubectl get secret gitlab-wildcard-tls-ca -ojsonpath='{.data.cfssl_ca}' | base64 --decode > ./files/gitlab-ca.pem

helm upgrade --install kube-agent gitlab/gitlab-agent \
    --namespace gitlab-agent-kube-agent \
    --create-namespace \
    --set image.tag=v17.1.2 \
    --set config.token=${AGENT_TOKEN} \
    --set config.kasAddress=wss://kas.${GITLAB_DOMAIN} \
    --set-file config.kasCaCert=./files/gitlab-ca.pem \
    --set "hostAliases[0].ip=${GITLAB_IP}" \
    --set "hostAliases[0].hostnames[0]=kas.${GITLAB_DOMAIN}"
