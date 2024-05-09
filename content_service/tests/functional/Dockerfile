FROM python:3.9-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

COPY . .

RUN apt-get update && apt-get -y install curl 
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["sh", "/app/entrypoint.prod.sh"]
