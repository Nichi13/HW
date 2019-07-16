create_table_text = '''
                CREATE TABLE found_people (
    id serial PRIMARY KEY,
    id_vk integer,
    first_name character varying(100),
    last_name character varying(100),
    interests text,
    movies  text,
    music  text,
    books  text,
    common_count smallint,
    common_group  text,
    recording_time timestamp);
            '''
insert_info_found_people_text = """
                INSERT INTO found_people (
                        id_vk, 
                        first_name, 
                        last_name,
                        interests,
                        movies,
                        music,
                        books,
                        common_count,
                        common_group,
                        recording_time)
                VALUES (
                        '%s',
                        $$%s$$,
                        $$%s$$,
                        $Q$%s$Q$,
                        $Q$%s$Q$,
                        $Q$%s$Q$,
                        $Q$%s$Q$,
                        '%s',
                        $$%s$$,
                        '%s');
            """

sort_found_people_text = """ WITH t AS (SELECT * FROM found_people ORDER BY id_vk DESC LIMIT 100)
                                SELECT
                                    * FROM t ORDER BY common_count DESC, common_group DESC;"""

create_table_photo_text = '''
                            CREATE TABLE photo_people (
                                id serial PRIMARY KEY,
                                id_vk integer,
                                likes integer,
                                URL  text);
                        '''

insert_info_photo_people_text = """
                                    INSERT INTO photo_people (
                                                id_vk,
                                                likes,
                                                URL)
                                    VALUES (
                                                '%s',
                                                '%s',
                                                $$%s$$);
                                """

sort_by_like_text = """SELECT * FROM photo_people WHERE id_vk = %s ORDER BY id_vk DESC, likes DESC;"""

create_table_photo_int_text = '''
                                CREATE TABLE photo_people_int (
                                    id serial PRIMARY KEY,
                                    id_vk numeric,
                                    likes numeric,
                                    URL  text);
                                '''

insert_int_by_like_text = """
                                  INSERT INTO
                                        photo_people_int (
                                            id_vk,
                                            likes,
                                            URL)
                                    VALUES (
                                        '%s',
                                        '%s',
                                        $$%s$$);
                            """

sort_int_by_like_text = """SELECT * FROM photo_people_int 
                                WHERE id_vk = %s ORDER BY id_vk DESC, likes DESC;"""