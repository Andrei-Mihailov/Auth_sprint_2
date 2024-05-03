import os
import json

from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import ConnectionError, TransportError
from backoff import on_exception, expo

from configs.config import ElasticsearchConfig
from utils.transform_data import prepare_data


class ElasticsearchSaver:
    def __init__(self, config: ElasticsearchConfig, batch_size=200):
        self.es = Elasticsearch(config['urls'])
        self.index = config['index']
        self.batch_size = batch_size
        self.clear_index = False
        # если индекса в эластике нет
        if not self.es.indices.exists(index=self.index):
            self.index_file = f'configs/{self.index}_schema.txt'
            if os.path.exists(self.index_file):
                with open(self.index_file, "r", encoding="utf-8") as f:
                    request_body = json.load(f)
                self.es.indices.create(
                    index=self.index, body=request_body)  # создаем индекс
                self.clear_index = True
            else:
                print(f'file {self.index_file} is not exist')

    @on_exception(expo, (ConnectionError, TransportError), max_tries=5)
    def save_data(self, data):
        """
        Сохраняет данные пачками в Elasticsearch.
        """
        processed_data = prepare_data(data)

        batches = [processed_data[i:i+self.batch_size]
                   for i in range(0, len(processed_data), self.batch_size)]
        for batch in batches:
            body = []
            for document in batch:
                action = {
                    "_index": self.index,
                    "_op_type": "index",
                    "_source": document,
                    "_id": document["id"]
                }
                body.append(action)
            helpers.bulk(self.es, body, request_timeout=30)
