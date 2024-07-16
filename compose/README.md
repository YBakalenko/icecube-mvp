docker compose up -d
docker compose down

docker buildx build --platform linux/amd64,linux/arm/v7,linux/arm64/v8 -t ybakalenko/icecube-train:0.3.1 --push icecube/train
docker buildx build --platform linux/amd64,linux/arm/v7,linux/arm64/v8 -t ybakalenko/icecube-predict:0.3.1 --push icecube/predict
docker buildx build --platform linux/amd64,linux/arm/v7,linux/arm64/v8 -t ybakalenko/icecube-streamlit:0.3.1 --push icecube/frontend