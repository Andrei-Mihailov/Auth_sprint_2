import sys
from os import path

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError as conn_err_es
import backoff

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import settings


@backoff.on_exception(backoff.expo, conn_err_es, max_time=60)
def connect_to_elastic():
    es_client = Elasticsearch(hosts=settings.test_settings.es_host,
                              validate_cert=False,
                              use_ssl=False,
                              request_timeout=1)
    es_client.info()


if __name__ == '__main__':
    connect_to_elastic()
