FROM python:3.12-slim-bookworm

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        cmake \
        build-essential \
        gcc \
        g++ \
        ninja-build && \
    pip install --upgrade pip && \
    pip install --ignore-installed -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV TRAIN_DATABASE_HOST=mongodb
ENV TRAIN_DATABASE_PORT=27017

# EXPOSE 18507
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "18507" , "--reload"]
