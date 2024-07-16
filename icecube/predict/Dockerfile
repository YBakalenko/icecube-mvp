FROM python:3.11-slim-buster

WORKDIR /app
#/predict
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

ENV PREDICT_DATABASE_HOST mongodb
ENV PREDICT_DATABASE_PORT 27017

# EXPOSE 9940
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9940" , "--reload"]
