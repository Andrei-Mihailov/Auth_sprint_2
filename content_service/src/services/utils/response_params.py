from models.models import Film, Genre, Person, PersonFilmDetails


def prepare_fields_for_response(model, instance):
    if model == Film:
        response_params_ = {
            "uuid": instance.id,
            "title": instance.title,
            "imdb_rating": instance.imdb_rating
            }
    elif model == Genre:
        response_params_ = {
            "uuid": instance.id,
            "name": instance.name
            }
    elif model == Person:
        response_params_ = {
            "uuid": instance.id,
            "full_name": instance.full_name,
            "films": [
                {
                    "uuid": p.id,
                    "roles": [
                        r.value for r in p.roles
                        ]
                }
                for p in instance.films
                ]
            }
    elif model == PersonFilmDetails:
        response_params_ = {
            "uuid": instance.id,
            "title": instance.title,
            "imdb_rating": instance.imdb_rating
            }
    return response_params_
