from crud.retrieve_user import user_retrieve, user_retrieve_all, user_exists_by_email, user_exists_by_id, user_search
from crud.create_user import db_create_user
from crud.delete_user import delete_user,delete_users_many
from crud.update_user import db_update_user
from connection import get_db_connection
import print_user as pu
import psycopg2
import re

menu = '''
Выберите операцию для выполнения в таблице 'users':
1. Вывести данные пользователя
2. Вывести всех пользователей
3. Создать нового пользователя
4. Удалить пользователя
5. Удалить нескольких пользователей
6. Обновить данные пользователя
7. Поиск пользователей
=============================
0. Выйти'''

connection = get_db_connection()





while True:
    print(menu)
    operation = input('ВЫБОР: ').strip()

    match operation:
        case '0':
            connection.close()
            print('Выход из приложения.')
            break

        case '1':
            try:
                user_id = int(input('Введите ID пользователя: '))
            except ValueError:
                print('Ошибка: ID должен быть числом')
                continue

            user = user_retrieve(connection, user_id)
            pu.print_users(user) if user else print(f'Пользователь с ID {user_id} не найден')

        case '2':
            users = user_retrieve_all(connection)
            pu.print_users(users) if users else print('В таблице нет пользователей')

        case '3':
            db_create_user(connection)

        case '4':
            try:
                user_id = int(input('Введите ID пользователя для удаления: '))
            except ValueError:
                print('Ошибка: ID должен быть числом')
                continue

            deleted = delete_user(connection, user_id)
            print(f'Пользователь {user_id} удален') if deleted else print(f'Пользователь {user_id} не найден')

        case '5':
            try:
                ids = input('Введите ID пользователей через пробел: ').split()
                user_ids = tuple(int(id) for id in ids)
            except ValueError:
                print('Ошибка: ID должны быть числами')
                continue

            deleted_count = delete_users_many(connection, user_ids)
            print(f'Удалено пользователей: {deleted_count}')

        case '6':
            db_update_user(connection)


        case '7':
            print('Введите параметры поиска (оставьте пустым для игнорирования)')
            last_name = input('Фамилия: ').strip()
            first_name = input('Имя: ').strip()
            email = input('Email: ').strip()

            try:
                limit = int(input('Лимит результатов (по умолчанию 5): ') or 5)
                offset = int(input('Смещение (по умолчанию 0): ') or 0)
            except ValueError:
                print('Ошибка: лимит и смещение должны быть числами')
                continue

            search_data = {
                'last_name': last_name,
                'first_name': first_name,
                'email': email
            }

            users = user_search(connection, search_data, limit, offset)
            pu.print_users(users) if users else print('Пользователи не найдены')

        case _:
            print('Неверная команда')