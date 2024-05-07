FROM python:3.9-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY ./auth_service/requirements.txt requirements.txt
COPY ./auth_service/alembic.ini alembic.ini

RUN apt-get update && apt-get -y install curl
RUN pip install --no-cache-dir -r requirements.txt

COPY ./auth_service/src ./src