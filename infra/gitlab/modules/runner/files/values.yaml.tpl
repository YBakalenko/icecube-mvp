gitlabUrl: https://${gitlab_host}/

# runnerRegistrationToken: "${runner_token}"
runnerToken: "${runner_token}"

certsSecretName: gitlab-wildcard-tls-chain

concurrent: 10

checkInterval: 30

hostAliases:
  - ip: "${gitlab_ip}"
    hostnames:
    - "${gitlab_host}"

serviceAccount:
  create: true

rbac:
  create: true
#  rules:
#    - apiGroups: [""]
#      resources: ["pods"]
#      verbs: ["list", "get", "watch", "create", "delete"]
#    - apiGroups: [""]
#      resources: ["pods/exec"]
#      verbs: ["create"]
#    - apiGroups: [""]
#      resources: ["pods/log"]
#      verbs: ["get"]
#    - apiGroups: [""]
#      resources: ["pods/attach"]
#      verbs: ["list", "get", "create", "delete", "update"]
#    - apiGroups: [""]
#      resources: ["secrets"]
#      verbs: ["list", "get", "create", "delete", "update"]
#    - apiGroups: [""]
#      resources: ["configmaps"]
#      verbs: ["list", "get", "create", "delete", "update"]

runners:
  privileged: true

  config: |
    [[runners]]
      [runners.kubernetes]
        tls_verify = false
        image = "ubuntu:20.04"
        privileged = true
      [[runners.kubernetes.volumes.empty_dir]]
        name = "docker-certs"
        mount_path = "/certs/client"
        medium = "Memory"
  executor: kubernetes
