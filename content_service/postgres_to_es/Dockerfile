#FROM python:3.8.6
FROM python:3.9-slim
WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get -y install curl && apt-get install wget
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN wget -O /usr/local/bin/wait-for-it.sh "https://github.com/vishnubob/wait-for-it/raw/master/wait-for-it.sh" \
     && chmod +x /usr/local/bin/wait-for-it.sh