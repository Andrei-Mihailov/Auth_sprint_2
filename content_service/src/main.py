import multiprocessing

import gunicorn.app.base

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch
from contextlib import asynccontextmanager

from core.config import settings
from db import elastic
from db import redis
from api.v1 import films, genres, persons


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    elastic.es = AsyncElasticsearch(
        hosts=[f'http://{settings.elastic_host}:{settings.elastic_port}'])
    yield
    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    description="Информация о фильмах, жанрах и людях, участвовавших в их создании",
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse
)


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


app.include_router(films.router, prefix='/api/v1/films')
app.include_router(genres.router, prefix='/api/v1/genres')
app.include_router(persons.router, prefix='/api/v1/persons')

if __name__ == '__main__':
    options = {
        "bind": "%s:%s" % ("0.0.0.0", "8000"),
        "workers": number_of_workers(),
        "worker_class": "uvicorn.workers.UvicornWorker"
    }

    StandaloneApplication(app, options).run()
