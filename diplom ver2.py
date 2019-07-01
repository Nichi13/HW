import requests
import json
import psycopg2
import re
import collections

TOKEN = '616abfd7ccc76114b3e9742e70bd66918aeece2aee635a5f994465bf44b30505b5b475922db82f5acb370'


class User():
    def __init__(self, access_token, id_vk):
        self.access_token = access_token
        self.id = id_vk

    def params(self):
        return {
            'access_token': self.access_token,
            'user_id': self.id,
            'extended': 0,
            'fields': 'bdate, books, city, country, interests, movies, music, relation, trending',
            'v': 5.92}

    def get_info(self):
        params = self.params()
        response = requests.get('https://api.vk.com/method/users.get', params)
        return response.json()['response']

    def get_friends(self):
        params = {
            'access_token': self.access_token,
            'user_id': self.id,
            'extended': 0,
            'v': 5.92}
        response = requests.get('https://api.vk.com/method/friends.get', params)
        return response.json()['response']['items']

    def get_groups(self):
        params = self.params()
        response = requests.get('https://api.vk.com/method/groups.get', params)
        return response.json()['response']

    def search(self):
        params = {
            'access_token': self.access_token,
            'user_id': self.id,
            'extended': 0,
            'city': '282',
            'v': 5.92}
        response = requests.get('https://api.vk.com/method/users.search', params)
        return response.json()['response']


def get_id():
    inp_id = input('Введите ID или Screen name ')
    try:
        id_final = int(inp_id)
    except ValueError:
        params = {'screen_name': inp_id,
                  'access_token': TOKEN,
                  'v': 5.92
                  }
        response = requests.get('https://api.vk.com/method/utils.resolveScreenName', params)
        id_final = response.json()['response']['object_id']
    return id_final


def params_for_search(id_info_vk):
    sex_input = input('Введите интересующий вас пол: М или Ж ')
    if sex_input == 'М':
        sex = '2'
    elif sex_input == 'Ж':
        sex = '1'
    else:
        sex = '0'
    status_input = input('Введите интересующее семейное положение: 1 - не женат (не замужем) 2 - в активном поиске')
    if status_input == '1':
        status = '1'
    elif status_input == '2':
        status = '6'
    else:
        status = ''
    age_from_input = input('Введите возраст от: ')
    age_to_input = input('до: ')
    try:
        country_id = id_info_vk[0]['country']['id']
        city_id = id_info_vk[0]['city']['id']
    except KeyError:
        country = input('Если ваша страна Россия, введите - 1, Украина - 2, Беларусь - 3')
        if country == '1':
            country_id = 1
            city_id = 1
        elif country == '2':
            country_id = 2
            city_id = 314
        elif country == '3':
            country_id = 3
            city_id = 282
        else:
            print('Попробуйте еще раз')
            exit()
    params = {
        'access_token': TOKEN,
        'user_id': id_l,
        'extended': 0,
        'sex': sex,
        'status': status,
        'city': city_id,
        'country': country_id,
        'age_from': age_from_input,
        'age_to': age_to_input,
        'count': 100,
        'v': 5.92,
        'sort': 0,
        'fields': 'books,common_count,interests,movies,music,'}
    response = requests.get('https://api.vk.com/method/users.search', params)
    return response.json()


def create_tables_found_people(conn):
        with conn.cursor() as cur:
            cur.execute('''
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
    common_group  text);
            ''')


def drop_tables_found_people(conn):
        with conn.cursor() as cur:
            cur.execute('''
                DROP TABLE found_people;
            ''')


def get_info_for_found_people(id_vvk, metod):
    params = {'access_token': TOKEN, 'user_id': id_vvk, 'extended': 0, 'v': 5.92}
    response = requests.get('https://api.vk.com/method/%s.get' %(metod), params)
    return response.json()['response']

def add_found_people(found_people_list_in_vk, conn):
    for item in found_people_list_in_vk:
        id_vk = (item['id'])
        try:
            common_friend = 0
            list_friend_for_found_people = get_info_for_found_people(id_vk, 'friends')
            for z in list_friend_for_found_people['items']:
                if z in friend_list:
                    common_friend += 1
        except KeyError:
            common_friend = 0
        try:
            list_group_for_found_people = get_info_for_found_people(id_vk, 'groups')
            common_group = ''
            for z in list_group_for_found_people['items']:
                if z in group_list['items']:
                    str_z = str(z)
                    common_group += str_z
                    common_group += ', '
        except KeyError:
            common_group = ''
        first_name = item['first_name']
        last_name = item['last_name']
        interests = item.get('interests')
        movies = item.get('movies')
        music = item.get('music')
        books = item.get('books')
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO found_people (id_vk, first_name, last_name,interests,movies,music,books,common_count,\
                common_group) VALUES ('%s',$$%s$$,$$%s$$,$Q$%s$Q$,$Q$%s$Q$,$Q$%s$Q$,$Q$%s$Q$,'%s',$$%s$$);
                """ % (id_vk, first_name, last_name, interests, movies, music, books, common_friend, common_group))
        print('...')


def sort_db_from_common_group_and_friends(conn):
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM found_people ORDER BY common_count DESC, common_group DESC;')
            records = cur.fetchall()
            return records

def create_photo_people_db():
    try:
        with conn.cursor() as cur:
            cur.execute('''
                    CREATE TABLE photo_people (
        id serial PRIMARY KEY,
        id_vk integer,
        likes integer,
        URL  text);
                ''')
    except psycopg2.errors.DuplicateTable:
        # with psycopg2.connect(
        #         "dbname ='found_people_db' user = 'postgres' password = '1'  host ='localhost'") as conn:
            print('Претенденты подобраны, а сейчас мы выбираем самые лучшие фото для Вас')


def get_photo(sort_list_for_f, conn):
    i = 0
    list_for_id =[]
    while i < 10:
        id_list = int(sort_list_for_f[i][1])
        list_for_id.append(int(sort_list_for_f[i][1]))
        params = {'access_token': TOKEN, 'owner_id': sort_list_for_f[i][1], 'album_id': 'profile',
                  'extended': 'likes', 'v': 5.92}
        response = requests.get('https://api.vk.com/method/photos.get', params)
        photo_info = response.json()
        try:
            for photo in photo_info['response']['items']:
                likes = (photo['likes']['count'])
                for c in (photo['sizes']):
                    url = (c['url'])
                with conn.cursor() as cur:
                    cur.execute("""
                                      INSERT INTO photo_people (id_vk,likes, URL) VALUES ('%s','%s',$$%s$$);
                               """ % (id_list, likes, url))
        except KeyError:
            print('')
        i += 1
    photo_dic = collections.defaultdict(list)
    for y in list_for_id:
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM photo_people WHERE id_vk = %s ORDER BY id_vk DESC, likes DESC;""" % (y))
            records = cur.fetchall()
            for x in records:
                photo_dic[int(x[1])].append(x[3])
    return photo_dic


def result_json(sort_list_vk):
    photo_list = get_photo(sort_list_vk, conn)
    result_file = []
    i = 0
    photo_limit = 3
    while i < 10:
        result = []
        id_l = int(sort_list_vk[i][1])
        result.append(id_l)
        for h in range(2, 10):
            result.append(sort_list_vk[i][h])
        for photo in photo_list[id_l][:photo_limit]:
            result.append(photo)
        i += 1
        result_file.append(result)
    print(result_file)
    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(result_file, file, indent=4, ensure_ascii=False)


def regexp(patern, text):
    res = re.search(patern, text, flags=re.IGNORECASE)
    if res is not None:
        result = 1
    else:
        result = 0
    return result

def create_photo_people_int_db():
    try:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE photo_people_int (
    id serial PRIMARY KEY,
    id_vk numeric,
    likes numeric,
    URL  text);
            ''')
    except psycopg2.errors.DuplicateTable:
            print('подбираем фото')

def sort_list_by_int(id_info, sort_list_vk):
    if id_info[0]['interests'] == '':
        interes_id = input('Введите ваши интересы, например: музыка')
    else:
        interes_id = id_info[0]['interests']
    sort_list_by_interest = []
    for q in sort_list_vk:
        res = regexp(interes_id, q[4])
        if res == 1:
            sort_list_by_interest.append(q)
    return sort_list_by_interest

def get_photo_int(sort_list_by_interest):
    i = 0
    list_for_id = []
    while i < 10:
        try:
            list_by_int = sort_list_by_interest[i][1]
            list_for_id.append(int(sort_list_by_interest[i][1]))
            params = {'access_token': TOKEN,
                      'owner_id': sort_list_by_interest[i][1],
                      'album_id': 'profile',
                      'extended': 'likes',
                      'v': 5.92}
            response = requests.get('https://api.vk.com/method/photos.get', params)
            x = response.json()
            for z in x['response']['items']:
                likes = ((z['likes']['count']))
                for c in (z['sizes']):
                    url = ((c['url']))
                with conn.cursor() as cur:
                    cur.execute("""
                                  INSERT INTO photo_people_int (id_vk,likes, URL) VALUES ('%s','%s',$$%s$$);
                               """ % (list_by_int, likes, url))
        except IndexError:
            print('...')
        i += 1
    photo_dic = collections.defaultdict(list)
    for y in list_for_id:
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM photo_people_int WHERE id_vk = %s ORDER BY id_vk DESC, likes DESC;""" % (y))
            records = cur.fetchall()
            for x in records:
                photo_dic[int(x[1])].append(x[3])
    return photo_dic

def result_interests(conn,sort_list_by_interest, photo_list):
    result_file = []
    photo_limit = 3
    i = 0
    try:
        while i < 10:
            result = []
            id_l = int(sort_list_by_interest[i][1])
            result.append(id_l)
            for h in range(2, 7):
                result.append(sort_list_by_interest[i][h])
            for photo in photo_list[id_l][:photo_limit]:
                result.append(photo)
            i += 1
            result_file.append(result)
    except IndexError:
        print('...')
    with open('result_int.json', 'w', encoding='utf-8') as file:
        json.dump(result_file, file, indent=4, ensure_ascii=False)
    print(result_file)


if __name__ == '__main__':
    with psycopg2.connect("dbname ='found_people_db' user = 'postgres' password = '1'  host ='localhost'") as conn:
        id_l = get_id()
        us = User(TOKEN, id_l)
        group_list = us.get_groups()
        friend_list = us.get_friends()
        id_info = us.get_info()
        found_people_list = (params_for_search(id_info)['response']['items'])
        print('Программа берет выборку 1000 пользователей и сохраняет в БД, поэтому работает ну ОЧЕНЬ долго!!! ')
        try:
            create_tables_found_people(conn)
        except psycopg2.errors.DuplicateTable:
            with psycopg2.connect(
                    "dbname ='found_people_db' user = 'postgres' password = '1'  host ='localhost'") as conn:
                drop_tables_found_people(conn)
                create_tables_found_people(conn)
        add_found_people(found_people_list, conn)
        sort_list = sort_db_from_common_group_and_friends(conn)
        create_photo_people_db()
        with psycopg2.connect(
                "dbname ='found_people_db' user = 'postgres' password = '1'  host ='localhost'") as conn:
            result_json(sort_list)
        print('Результат вы найдете в json файле')
        x = input('Если вы хотите продолжить поиск по вашим интересам введите 1 ')
        if x == '1':
            with psycopg2.connect(
                    "dbname ='found_people_db' user = 'postgres' password = '1'  host ='localhost'") as conn:
                create_photo_people_int_db()
            sort_list_by_interest = sort_list_by_int(id_info, sort_list)
            photo_list = get_photo_int(sort_list_by_interest)
            result_interests(conn, sort_list_by_interest, photo_list)
