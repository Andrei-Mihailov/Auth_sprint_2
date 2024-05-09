## Описание основных сервисов

auth_service - отвечает за аутентификацию пользователей. Стек: FastApi, Redis, Postgres, Jaeger
admin_service - отвечает за наполнение данными базы фильмов. Стек: Django, Postgres
content_service - отвечает за работу с пользовательскими запросами. Стек: FastApi, Redis, Postgres, Elastic

etl (genres, films, persons) - осуществляет перенос данных из admin_service в content_service

## Доступ в панель администратора

Необходимо создать суперпользователя консольной командой в auth-service. Под ним осуществляем вход

```
python src/main.py --email=email --password=password
```

## Доступ к контект сервису

Производим аутентификацию в auth-service, копируем из cookies access_token, добавляем его в авторизацию

```
/auth/api/v1/users/login
```

## Работа с сервисами через docker

http://127.0.0.1/auth/api/openapi
http://127.0.0.1/movies/api/openapi
http://127.0.0.1/admin/

## Регистрация и аутентификация через Яндекс

Переход по ссылке

```
http://127.0.0.1/auth/api/v1/oauth/yandex/authorize-url
```

перенаправит на страницу авторизации яндекса, после чего полученный код необходимо передать в ручку:

```
/auth/api/v1/oauth/webhook
```

## Партицирование

Выполнено партицирование таблицы authentication по дате авторизации в разрезе месяцев.
Реализация в миграции alembic:
2024_05_05_0529-65a4e8f17754_add_partition_to_auth
Автоматическое создание партиций с использованием pg_partman

## Ссылка на репозиторий:

```
https://github.com/Andrei-Mihailov/Auth_sprint_2
```
