import sys


def prepare_data(data):
    """
    Подготовка данных перед записью в Elasticsearch
    """
    processed_data = []
    schema = sys.argv[1]
    for record in data:
        if schema == 'films':
            document = {
                "id": record["film_work_id"],
                "imdb_rating": record["film_work_rating"],
                "title": record["film_work_title"],
                "description": record["film_work_description"],
                "actors_names": [
                    actor['name']
                    for actor in record["actors"]
                ] if record["actors"] else '',
                "writers_names": [
                    writer['name']
                    for writer in record["writers"]
                ] if record["writers"] else '',
                "directors_names": [
                    director['name']
                    for director in record["directors"]
                ] if record["directors"] else '',
                "genres": [
                    {
                        "id": genre['id'],
                        "name": genre['name']
                    }
                    for genre in record["genres"]
                ] if record["genres"] else [],
                "actors": [
                    {
                        "id": actor['id'],
                        "name": actor['name']
                    }
                    for actor in record["actors"]
                ] if record["actors"] else [],
                "writers": [
                    {
                        "id": writer['id'],
                        "name": writer['name']
                    }
                    for writer in record["writers"]
                ] if record["writers"] else [],
                "directors": [
                    {
                        "id": director['id'],
                        "name": director['name']
                    }
                    for director in record["directors"]
                ] if record["directors"] else [],
            }
        elif schema == 'genres':
            record = record[0]
            document = {
                "id": record["id"],
                "name": record["name"],
            }
        elif schema == 'persons':
            document = {
                "id": record["id"],
                "full_name": record["name"],
                "films": record["films"]
            }
        processed_data.append(document)
    return processed_data
