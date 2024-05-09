get_count_data_from_table = "SELECT count(*) FROM content.filmwork"

get_all_data_from_table = """SELECT
    fw.id AS film_work_id,
    fw.title AS film_work_title,
    fw.description AS film_work_description,
    fw.creation_date AS film_work_creation_date,
    fw.rating AS film_work_rating,
    fw.type_film AS film_work_type,
    ARRAY_AGG(DISTINCT CASE WHEN pfw.role = 'actor' THEN p.id END) AS actors_id,
    ARRAY_AGG(DISTINCT CASE WHEN pfw.role = 'actor' THEN p.full_name END) AS actors,
    ARRAY_AGG(DISTINCT CASE WHEN pfw.role = 'writer' THEN p.id END) AS writers_id,
    ARRAY_AGG(DISTINCT CASE WHEN pfw.role = 'writer' THEN p.full_name END) AS writers,
    ARRAY_AGG(DISTINCT CASE WHEN pfw.role = 'director' THEN p.id END) AS directors_id,
    ARRAY_AGG(DISTINCT CASE WHEN pfw.role = 'director' THEN p.full_name END) AS directors,
    ARRAY_AGG(DISTINCT g.id) AS genre_id,
    ARRAY_AGG(DISTINCT g.name) AS genre_name
FROM
    content.filmwork fw
LEFT JOIN
    content.person_film_work pfw ON fw.id = pfw.film_work_id
LEFT JOIN
    content.person p ON pfw.person_id = p.id
LEFT JOIN
    content.genre_film_work gfw ON fw.id = gfw.film_work_id
LEFT JOIN
    content.genre g ON gfw.genre_id = g.id
GROUP BY
    fw.id,
    fw.title,
    fw.description,
    fw.creation_date,
    fw.rating,
    fw.type_film
ORDER BY
    fw.id
OFFSET {offset} LIMIT {limit};
"""
