# Реализация API-онлайн кинотеатра

Используются в докер-контейнерах:

- Postgres 13
- Elasticsearch 8.6.2
- Redis 7.2.4

Реализованы сервисы:

- solution-fastapi - реализация api кинотеатра на основе данных elastic
- etl-genres, etl-films, etl-persons - elt для записи данных из pg в elastic

## Порядок работы

1. Cоздать .env файл на основе template.env
2. Выполнить команды

```console
$ docker-compose build
$ docker-compose up
```
