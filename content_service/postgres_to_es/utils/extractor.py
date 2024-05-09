import psycopg2

from psycopg2.extensions import connection as _connection
from backoff import on_exception, expo
from psycopg2.extras import DictCursor
from contextlib import contextmanager

from utils.queries import (get_data_from_table,
                           get_count_data_from_table)
from configs.config import schema_to_transfer


@contextmanager
def psycopg2_context(dsl):
    conn = psycopg2.connect(**dsl, cursor_factory=DictCursor)
    try:
        yield conn
    finally:
        conn.close()


class PostgresExtractor:
    def __init__(self, pg_conn: _connection):
        """
        Создает подключение к базе данных PostgreSQL.
        """
        self.conn: _connection = pg_conn

    @on_exception(expo, (psycopg2.DatabaseError, psycopg2.OperationalError), max_tries=5)
    def get_table_size(self):
        """
        Получает размер указанной таблицы в базе данных PostgreSQL.
        """
        cursor = self.conn.cursor()

        query = get_count_data_from_table[schema_to_transfer]
        cursor.execute(query)

        size = cursor.fetchone()[0]

        cursor.close()

        return size

    @on_exception(expo, (psycopg2.DatabaseError, psycopg2.OperationalError), max_tries=5)
    def extract_data(self, offset, limit):
        """
        Извлекает данные из указанной таблицы с использованием смещения и лимита.
        """
        cursor = self.conn.cursor()

        query = get_data_from_table[schema_to_transfer].format(offset=offset,
                                                               limit=limit)
        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()

        return results
