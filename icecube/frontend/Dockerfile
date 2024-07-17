FROM python:3.11-slim-buster

WORKDIR /app
#/frontend
COPY . .


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        cmake \
        build-essential \
        gcc

RUN pip install --upgrade pip && \
    pip install --ignore-installed -r requirements.txt


# EXPOSE 8080
ENV TRAIN_SERVICE_HOST=train
ENV TRAIN_SERVICE_PORT=18507
ENV PREDICT_SERVICE_HOST=predict
ENV PREDICT_SERVICE_PORT=9940

ENTRYPOINT ["streamlit","run"]
CMD ["main.py"]
