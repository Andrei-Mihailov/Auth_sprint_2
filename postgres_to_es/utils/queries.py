get_count_data_from_table = {
    "films": "SELECT count(*) FROM content.film_work",
    "genres": "SELECT count(*) FROM content.genre",
    "persons": "SELECT count(*) FROM content.person"
}

get_data_from_table = {
    "films": """SELECT
                fw.id AS film_work_id,
                fw.title AS film_work_title,
                fw.description AS film_work_description,
                fw.creation_date AS film_work_creation_date,
                fw.rating AS film_work_rating,
                fw.type AS film_work_type,
                ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id,'name', p.full_name)) FILTER
                    (WHERE pfw.role = 'actor') AS actors,
                ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id,'name', p.full_name)) FILTER
                    (WHERE pfw.role = 'writer') AS writers,
                ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id,'name', p.full_name)) FILTER
                    (WHERE pfw.role = 'director') AS directors,
                ARRAY_AGG(DISTINCT jsonb_build_object('id', g.id, 'name', g.name)) AS genres
            FROM
                content.film_work fw
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
                fw.type
            ORDER BY
                fw.id
            OFFSET {offset} LIMIT {limit};
            """,
    "genres": """SELECT
                jsonb_build_object('id', g.id, 'name', g.name) AS genres
            FROM
                content.genre g
            OFFSET {offset} LIMIT {limit};
            """,
    "persons": """SELECT
                    p.id,
                    p.full_name AS name,
                    jsonb_agg(jsonb_build_object('id', pfw.film_work_id,
                    'title', fw.title, 'imdb_rating', fw.rating, 'roles',
                    pfw.roles_agg)) AS films
                FROM
                    content.person p
                LEFT JOIN (
                    SELECT
                        pfw.person_id,
                        pfw.film_work_id,
                        fw.title,
                        fw.rating,
                        jsonb_agg(DISTINCT pfw.role) AS roles_agg
                    FROM
                        content.person_film_work pfw
                    LEFT JOIN content.film_work fw ON pfw.film_work_id = fw.id
                    GROUP BY
                        pfw.person_id,
                        pfw.film_work_id,
                        fw.title,
                        fw.rating
                ) pfw ON p.id = pfw.person_id
                LEFT JOIN content.film_work fw ON pfw.film_work_id = fw.id
                GROUP BY
                    p.id,
                    p.full_name
                OFFSET {offset} LIMIT {limit};
            """
}
