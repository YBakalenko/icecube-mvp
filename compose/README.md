1. Просто выполнить запуск проекта с помощью Docker engine
```
docker compose up -d
docker compose down
```
2. Если необходимо отдельно выполнить сборку образов компонентов приложения:
```
docker buildx build --platform linux/amd64,linux/arm64 -t ybakalenko/icecube-train:0.3.1 --push icecube/train
docker buildx build --platform linux/amd64,linux/arm64 -t ybakalenko/icecube-predict:0.3.1 --push icecube/predict
docker buildx build --platform linux/amd64,linux/arm64 -t ybakalenko/icecube-streamlit:0.3.1 --push icecube/frontend
```