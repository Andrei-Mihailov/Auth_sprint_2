import os
import logging
import json
import time

from dotenv import load_dotenv

from utils.extractor import PostgresExtractor, psycopg2_context
from utils.saver import ElasticsearchSaver
from configs.config import postgres_config_data, elasticsearch_config_data, schema_to_transfer


class DataMigrator:
    def __init__(self, extractor, saver, state_file=f"{schema_to_transfer}_state.json"):
        self.extractor: PostgresExtractor = extractor
        self.saver: ElasticsearchSaver = saver
        self.state_file = state_file

    def load_state(self):
        """
        Загружает состояние из файла.
        """
        state = {"offset": 0}
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                state = json.load(f)
        return state

    def save_state(self, state):
        """
        Сохраняет состояние в файл.
        """
        with open(self.state_file, "w") as f:
            json.dump(state, f)

    def migrate_data(self, offset):
        """
        Выполняет миграцию данных из PostgreSQL в Elasticsearch.
        """

        table_size = self.extractor.get_table_size()

        try:
            next_offset = offset
            while next_offset < table_size:
                logging.info(f"Миграция данных со смещением {next_offset}")
                limit = min(table_size - next_offset,
                            self.saver.batch_size)
                results = self.extractor.extract_data(
                    next_offset, limit)
                if not results:
                    break

                self.saver.save_data(results)
                next_offset += limit

                state["offset"] = next_offset
                self.save_state(state)

            offset = 0
        except Exception as e:
            logging.error(
                f"Ошибка миграции данных: {str(e)}")
            self.saver.es.close()  # закрываем соединение в случае исключений
            logging.info("Повторная попытка через 60 секунд...")
            time.sleep(60)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    while True:
        with psycopg2_context(postgres_config_data.model_dump()) as pg_conn:
            extractor = PostgresExtractor(pg_conn)
            saver = ElasticsearchSaver(elasticsearch_config_data.model_dump())

            migrator = DataMigrator(extractor, saver)

            # загружаем состояние и определяем таблицу и смещение копирования
            state = migrator.load_state()
            if saver.clear_index:
                offset = 0
                state["offset"] = offset
                migrator.save_state(state)
            else:
                offset = state["offset"]
            migrator.migrate_data(offset)
            logging.info("Перенос данных успешно завершен!")
        time.sleep(30)
