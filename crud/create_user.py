from crud.retrieve_user import user_exists_by_email
import print_user as pu
import psycopg2
import re

def capitalize_name(name):
    """Приводит имя к виду с заглавной первой буквой, остальные - строчные"""
    if not name:
        return name
    return name[0].upper() + name[1:].lower()

def validate_name(name: str, field_name: str, is_required: bool = True) -> bool:
    if not name:
        if is_required:
            print(f'Ошибка: поле {field_name} не может быть пустым')
            return False
        return True
    
    # Изменено: разрешаем только апостроф ’ (U+2019) и запрещаем прямой апостроф '
    if not re.match(r'^[А-Яа-яЁё’"\u2018\u2019\u201B\u2032\u2035\s\-.,()]+$', name):
        print(f'Ошибка: поле {field_name} содержит недопустимые символы. '
              f'Допустимы только русские буквы, апострофы (’), дефисы, пробелы, точки, запятые и скобки')
        return False
    
    # Проверка что есть хотя бы одна буква (не только спецсимволы)
    if not re.search(r'[А-Яа-яЁё]', name):
        print(f'Ошибка: поле {field_name} должно содержать хотя бы одну букву')
        return False
    
    # Проверка на двойные пробелы и другие повторяющиеся спецсимволы
    if re.search(r'([.\-’ ,()])\1', name):  # Убрал прямой апостроф из проверки
        print(f'Ошибка: поле {field_name} содержит повторяющиеся специальные символы подряд')
        return False
    
    # Проверка на недопустимые комбинации спецсимволов
    if re.search(r'[.\-’,()]{2,}', name):  # Убрал прямой апостроф из проверки
        print(f'Ошибка: поле {field_name} содержит недопустимые сочетания специальных символов')
        return False
    
    # Проверки для фамилии
    if field_name.lower() == 'фамилия':
        if name[0] in ('.', '-', '’', ' ', ',', ')'):  # Заменил прямой апостроф на ’
            print(f'Ошибка: фамилия не может начинаться с символа "{name[0]}"')
            return False
        if name[-1] in ('.', '-', '’', ' ', ',', '('):  # Заменил прямой апостроф на ’
            print(f'Ошибка: фамилия не может заканчиваться символом "{name[-1]}"')
            return False
        if len(name) == 1 and name in ('.', '-', '’', ' ', ',', '(', ')'):  # Заменил прямой апостроф на ’
            print(f'Ошибка: фамилия не может состоять только из символа "{name}"')
            return False
    
    # Проверки для имени и отчества
    if field_name.lower() in ('имя', 'отчество'):
        if name[0] in ('-', '’', ' ', ',', '.', ')'):  # Заменил прямой апостроф на ’
            print(f'Ошибка: {field_name} не может начинаться с символа "{name[0]}"')
            return False
        if name[-1] in ('-', '’', ' ', ',', '('):  # Заменил прямой апостроф на ’
            print(f'Ошибка: {field_name} не может заканчиваться символом "{name[-1]}"')
            return False
        if len(name) == 1 and name in ('-', '’', ' ', ',', '.', '(', ')'):  # Заменил прямой апостроф на ’
            print(f'Ошибка: {field_name} не может состоять только из символа "{name}"')
            return False
    
    
    if '(' in name or ')' in name:
        stack = []
        for i, char in enumerate(name):
            if char == '(':
                stack.append(i)
            elif char == ')':
                if not stack:
                    print(f'Ошибка: поле {field_name} содержит непраные скобки')
                    return False
                stack.pop()
                
    # Проверка на непарные скобки
    if name.count('(') != name.count(')'):
        print(f'Ошибка: поле {field_name} содержит непарные скобки')
        return False
    
    # Проверка на латинские буквы I, V
    if re.search(r'[IViv]', name):
        print(f'Ошибка: поле {field_name} содержит недопустимые латинские буквы (I, V)')
        return False
    if name[0].upper() in ('I', 'V'):
        print(f'Ошибка: поле {field_name} не может начинаться с латинской буквы {name[0].upper()}')
        return False
    
    return True

def validate_email(email: str) -> bool:
    """Проверяет корректность email согласно требованиям БД"""
    if not email:
        print('Ошибка: email не может быть пустым')
        return False
    
    email = email.strip()
    if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', email, re.IGNORECASE):
        print('Ошибка: некорректный формат email')
        return False
    
    return True

def validate_password(password: str) -> bool:
    """Проверяет сложность пароля согласно требованиям БД"""
    if not password:
        print('Ошибка: пароль не может быть пустым')
        return False
    
    if len(password) < 8:
        print('Ошибка: пароль должен содержать минимум 8 символов')
        return False
    
    if not re.search(r'[A-Z]', password):
        print('Ошибка: пароль должен содержать хотя бы одну заглавную букву')
        return False
    
    if not re.search(r'[a-z]', password):
        print('Ошибка: пароль должен содержать хотя бы одну строчную букву')
        return False
    
    if not re.search(r'[0-9]', password):
        print('Ошибка: пароль должен содержать хотя бы одну цифру')
        return False
    
    if not re.search(r'[^A-Za-z0-9]', password):
        print('Ошибка: пароль должен содержать хотя бы один специальный символ')
        return False
    
    return True

def get_valid_input(prompt: str, validator: callable, *args) -> str:
    """Получает валидный ввод от пользователя с немедленной проверкой"""
    while True:
        value = input(prompt).strip()
        if validator(value, *args):
            return value

# НОВАЯ ФУНКЦИЯ ДЛЯ ВСТАВКИ В БД
def _insert_user_to_db(connection, user_data) -> int:
    """
    Вставляет данные пользователя в базу данных.
    Возвращает ID созданного пользователя.
    Предполагается, что данные уже валидированы.
    """
    try:
        cursor = connection.cursor()
        sql = """
            INSERT INTO users (last_name, first_name, middle_name, email, password)
            VALUES (%s, %s, %s, %s, %s) RETURNING user_id;
        """
        cursor.execute(sql, (
            user_data['last_name'],
            user_data['first_name'],
            user_data.get('middle_name'), # Используем .get() для необязательного поля
            user_data['email'],
            user_data['password']
        ))
        user_id = cursor.fetchone()[0]
        connection.commit()
        cursor.close()
        return user_id
    except psycopg2.Error as e:
        connection.rollback()
        # Вместо print, лучше перебросить исключение, чтобы вызывающий код мог его обработать
        raise e

# ИЗМЕНЕННАЯ ФУНКЦИЯ db_create_user
def db_create_user(connection) -> None:
    """Процесс создания пользователя с валидацией всех полей"""
    print("\nСоздание нового пользователя")
    
    last_name = get_valid_input("Фамилия: ", validate_name, "фамилия")
    first_name = get_valid_input("Имя: ", validate_name, "имя")
    
    middle_name = get_valid_input(
        "Отчество (необязательно): ", 
        validate_name, 
        "отчество", 
        False
    ) or None # Если ввод пустой, None
    
    email = get_valid_input("Email: ", validate_email)
    
    # Проверка уникальности email
    if user_exists_by_email(connection, email):
        print('Ошибка: пользователь с таким email уже существует')
        return
    
    password = get_valid_input("Пароль: ", validate_password)
    
    user_data = {
        'last_name': capitalize_name(last_name),  # Применяем форматирование
        'first_name': capitalize_name(first_name), # Применяем форматирование
        'middle_name': capitalize_name(middle_name) if middle_name else None, # Применяем форматирование
        'email': email.lower(), # Приводим email к нижнему регистру для консистентности
        'password': password
    }
    
    try:
        # Вызываем НОВУЮ функцию для вставки в БД
        user_id = _insert_user_to_db(connection, user_data) 
        print(f"\nПользователь успешно создан с ID: {user_id}")
    except Exception as e:
        print(f"\nОшибка при создании пользователя: {e}")
