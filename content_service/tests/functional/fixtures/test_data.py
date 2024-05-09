import pytest_asyncio
import uuid
import random
import sys
from os import path


sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from settings import test_settings


@pytest_asyncio.fixture()
def genres_data():
    letters = 'abcdefghijklmnopqrstuvwxyz'

    data = [{
        'id': str(uuid.uuid4()),
        'name': ''.join(random.sample(letters, 5))
    } for _ in range(59)]

    data.append({
        'id': test_settings.es_genre_id_field,
        'name': 'Action'
    })

    bulk_query: list[dict] = []
    for row in data:
        data = {'_index': test_settings.es_genre_index, '_id': row['id']}
        data.update({'_source': row})
        bulk_query.append(data)

    return bulk_query


@pytest_asyncio.fixture()
def persons_data():
    data = [{
        'id': str(uuid.uuid4()),
        'full_name': 'Stan',
        'films': [
            {
                'id': str(uuid.uuid4()),
                'imdb_rating': 8.5,
                'title': 'The Star',
                'roles': ['actor', 'writer']
            },
            {
                'id': str(uuid.uuid4()),
                'imdb_rating': 8.5,
                'title': 'The Star',
                'roles': ['actor', 'director']
            },
        ]
    } for _ in range(59)]

    data.append({
        'id': test_settings.es_person_id_field,
        'full_name': 'Stan',
        'films': [
            {
                'id': str(uuid.uuid4()),
                'imdb_rating': 8.5,
                'title': 'The Star',
                'roles': ['actor', 'writer']
            },
            {
                'id': str(uuid.uuid4()),
                'imdb_rating': 8.5,
                'title': 'The Star',
                'roles': ['actor', 'director']
            },
        ]
    })

    bulk_query: list[dict] = []
    for row in data:
        data = {'_index': test_settings.es_person_index, '_id': row['id']}
        data.update({'_source': row})
        bulk_query.append(data)

    return bulk_query


@pytest_asyncio.fixture()
def films_data():
    es_data = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genres': [
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f96', 'name': 'Action'},
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f97', 'name': 'Sci-Fi'}
        ],
        'title': 'The Star',
        'description': 'New World',
        'directors_names': ['Ann', 'Bob'],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'directors': [
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
            {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'}
        ],
        'actors': [
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
            {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'}
        ],
        'writers': [
            {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
            {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Howard'}
        ]
    } for _ in range(60)]

    es_data.append({
        'id': test_settings.es_film_id_field,
        'imdb_rating': 8.0,
        'genres': [
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f96', 'name': 'Action'},
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f97', 'name': 'Sci-Fi'}
        ],
        'title': 'The Star',
        'description': 'New World',
        'directors_names': ['Ann', 'Bob'],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'directors': [
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
            {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'}
        ],
        'actors': [
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
            {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'}
        ],
        'writers': [
            {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
            {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Howard'}
        ]
    }
    )

    bulk_query: list[dict] = []
    for row in es_data:
        data = {'_index': test_settings.es_film_index, '_id': row['id']}
        data.update({'_source': row})
        bulk_query.append(data)

    return bulk_query
