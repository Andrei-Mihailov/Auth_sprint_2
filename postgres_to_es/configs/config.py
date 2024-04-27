from pydantic import BaseModel
from pydantic_settings import BaseSettings
import sys


class Settings(BaseSettings):
    ELASTIC_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    ES_JAVA_OPTS: str
    SECURITY: str
    DISCOVERY: str

    class Config:
        env_file = ".env"


class PostgreSQLConfig(BaseModel):
    dbname: str
    user: str
    password: str
    host: str
    port: int


class ElasticsearchConfig(BaseModel):
    urls: str
    index: str


settings = Settings()

schema_to_transfer = sys.argv[1]

elasticsearch_config_data = ElasticsearchConfig(
    urls=f"http://{settings.ELASTIC_HOST}:9200",
    index=schema_to_transfer
)

postgres_config_data = PostgreSQLConfig(
    dbname=settings.DB_NAME,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=5432
)
