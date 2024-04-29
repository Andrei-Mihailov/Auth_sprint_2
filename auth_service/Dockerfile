FROM python:3.12-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt
COPY alembic.ini alembic.ini

RUN apt-get update && apt-get -y install curl
RUN pip install --upgrade pip
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs -o rustup.sh
RUN apt install rustc cargo -y 
RUN apt install --reinstall ca-certificates
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src