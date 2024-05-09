## Порядок работы

1. Cоздать .env файл на основе template.env
2. Cоздать .dev.env файл на основе template.dev.env
3. Выполнить команды

для запуска тестов в докере:

```console
$ docker-compose build
$ docker-compose up
```

для локального запуска тестов использовать команду:
pytest -v src
