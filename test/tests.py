import unittest
import requests
from diplom import drop_tables_found_people, create_tables_found_people, sort_db_from_common_group_and_friends
import psycopg2

class CaseTests (unittest.TestCase):

    def test_vk_response(self):
        TOKEN = '616abfd7ccc76114b3e9742e70bd66918aeece2aee635a5f994465bf44b30505b5b475922db82f5acb370'
        params = {
            'access_token': TOKEN,
            'user_id': '14897400',
            'extended': 0,
            'fields': 'bdate, books, city, country, interests, movies, music, relation, trending',
            'v': 5.92}
        response = requests.get('https://api.vk.com/method/users.get', params)
        print(response.status_code)
        self.assertEqual(response.status_code, 200, 'Не соответствует код запроса')
        t = response.json()
        print(t)

    def test_vk_autorization_failed(self):
        TOKEN = '616abfd7ccc714b3e97918aeece2aee635a5f994465bf44b30505b5b475922db82f5acb370'
        params = {
            'access_token': TOKEN,
            'user_id': '14897400',
            'extended': 0,
            'fields': 'bdate, books, city, country, interests, movies, music, relation, trending',
            'v': 5.92}
        response = requests.get('https://api.vk.com/method/users.get', params)
        t = response.json()
        print(t['error']['error_msg'])
        self.assertEqual(t['error']['error_msg'], 'User authorization failed: invalid access_token (4).', 'Не соответствует код запроса')

    def test_sort_db(self):
        with psycopg2.connect("dbname ='found_people_db' user = 'postgres' password = '1'  host ='localhost'") as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM found_people')
                records1 = cur.fetchall()
        with psycopg2.connect("dbname ='found_people_db' user = 'postgres' password = '1'  host ='localhost'") as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM found_people ORDER BY common_count DESC, common_group DESC;')
                records2 = cur.fetchall()
        self.assertNotEqual(records1, records2, 'Сортировка БД не работает')

    def test_double_create_data_base(self):
        create_tables_found_people()
        create_tables_found_people()
#       это можно считать отрицательным тестом? проверка того  что база данных создается

    def test_create_del_db(self):
        drop_tables_found_people()
        create_tables_found_people()
        drop_tables_found_people()
        create_tables_found_people()

