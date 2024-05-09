import uuid

from os import environ as env
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


load_dotenv(".dev.env")  # Загрузка переменных среды из файла `.env`


class TestSettings(BaseSettings):
    es_host: str = Field(
        default=f'http://{env.get("ELASTIC_HOST")}:{env.get("ELASTIC_PORT")}')

    es_film_id_field: str = '9e49073c-2b24-4026-9a27-7f9e5d69d23b'
    es_film_index: str = Field(default='films')
    es_film_mapping: str = Field(
        default=f'testdata/{es_film_index}_schema.txt')

    es_person_id_field: str = 'dc684ff5-719b-43f4-ba2c-43e0f58eb802'
    es_person_index: str = Field(default='persons')
    es_person_mapping: str = Field(
        default=f'testdata/{es_person_index}_schema.txt')

    es_genre_id_field: str = 'afb9353b-e33e-4a3c-8ae3-59fc5481da80'
    es_genre_index: str = Field(default='genres')
    es_genre_mapping: str = Field(
        default=f'testdata/{es_genre_index}_schema.txt')

    redis_host: str = Field(default={env.get("REDIS_HOST")})
    redis_port: str = Field(default={env.get("REDIS_PORT")})

    service_url: str = Field(
        default=f'http://{env.get("SERVICE_HOST")}:{env.get("SERVICE_PORT")}')


test_settings = TestSettings()
