## Setup Icecube app
1. Deploy xginx ingress controller
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```
2. Update dependencies
```
cd chart/icecube
helm dep update
```
3. Deploy application
```
helm install icecube ./icecube
```
Or:
```
helm upgrade --install icecube ./icecube
```
4. Deploy Prometheus stack
```
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack -f prometheus/values.yaml
```
