FROM python:3.11-slim-buster

WORKDIR /app
#/train
COPY . .


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        cmake \
        build-essential \
        gcc \
        g++


RUN pip install --upgrade pip && \
    pip install --ignore-installed -r requirements.txt

ENV TRAIN_DATABASE_HOST=mongodb
ENV TRAIN_DATABASE_PORT=27017

# EXPOSE 18507
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "18507" , "--reload"]
