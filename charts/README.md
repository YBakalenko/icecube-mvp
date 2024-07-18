## Setup Icecube app
1. Update dependencies
```
cd chart/icecube
helm dep update
```
2. Deploy application
```
helm install icecube ./icecube
```
Or:
```
helm upgrade --install icecube ./icecube
```
3. Deploy Prometheus stack
```
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack -f prometheus/values.yaml
```
