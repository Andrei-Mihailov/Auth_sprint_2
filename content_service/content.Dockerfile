FROM python:3.9-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY ./content_service/requirements.txt requirements.txt

RUN apt-get update && apt-get -y install curl
RUN pip install --no-cache-dir -r requirements.txt

COPY ./content_service/src ./src