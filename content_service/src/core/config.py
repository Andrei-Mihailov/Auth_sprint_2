import os
from logging import config as logging_config
from pydantic import BaseModel
from pydantic_settings import BaseSettings


from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    project_name: str

    # Настройки Elasticsearch
    elastic_host: str
    elastic_port: int
    es_java_opts: str
    security: str
    discovery: str

    # Настройки postgres
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int

    # Настройки Redis
    redis_host: str
    redis_port: int

    class Config:
        env_file = ".env"


settings = Settings()

page_max_size = 100
# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ElasticsearchConfig(BaseModel):
    urls: str
    index: str


class PostgreSQLConfig(BaseModel):
    dbname: str
    user: str
    password: str
    host: str
    port: int


els_config_films_data = ElasticsearchConfig(
    urls=f"http://{settings.elastic_host}:{settings.elastic_port}",
    index='films'
)

els_config_genres_data = ElasticsearchConfig(
    urls=f"http://{settings.elastic_host}:{settings.elastic_port}",
    index='genres'
)

els_config_persons_data = ElasticsearchConfig(
    urls=f"http://{settings.elastic_host}:{settings.elastic_port}",
    index='persons'
)

pg_config_data = PostgreSQLConfig(
    dbname=settings.db_name,
    user=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port
)
