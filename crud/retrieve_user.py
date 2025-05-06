from psycopg2 import sql
import re

def user_retrieve(connection, user_id: int) -> list:
    """Возвращает запись пользователя по ID"""
    cursor = connection.cursor()
    query = '''
        SELECT user_id, first_name, last_name, middle_name, email, password
        FROM users
        WHERE user_id = %s;
    '''
    try:
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()
        return result
    finally:
        cursor.close()


def user_retrieve_all(connection) -> list:
    """Возвращает всех пользователей"""
    cursor = connection.cursor()
    query = '''
        SELECT user_id, first_name, last_name, middle_name, email, password
        FROM users;
    '''
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    finally:
        cursor.close()


def user_exists_by_id(connection, user_id: int) -> bool:
    """Проверяет существование пользователя по ID"""
    cursor = connection.cursor()
    query = '''
        SELECT EXISTS (
            SELECT TRUE
            FROM users
            WHERE user_id = %s
        );
    '''
    try:
        cursor.execute(query, (user_id,))
        return cursor.fetchone()[0]
    finally:
        cursor.close()


def user_exists_by_email(connection, email: str) -> str|None:
    """Проверяет существование пользователя по email"""
    cursor = connection.cursor()
    query = '''
        SELECT email
        FROM users
        WHERE LOWER(email) = LOWER(%s);
    '''
    try:
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()


def user_search(
    connection, 
    search_data: dict, 
    limit: int = 5, 
    offset: int = 0, 
    sort_field: str = 'user_id',
    include_password: bool = False  # По умолчанию не возвращаем пароль
) -> list:
    """Поиск пользователей с фильтрацией
    
    Args:
        connection: Подключение к БД
        search_data: Словарь параметров поиска (может содержать first_name, last_name, 
                    middle_name, email)
        limit: Максимальное количество результатов
        offset: Смещение для пагинации
        sort_field: Поле для сортировки
        include_password: Включать ли пароль в результаты (не рекомендуется)
    
    Returns:
        Список найденных пользователей
    """
    cursor = connection.cursor()
    
    # Определяем поля для выборки
    select_fields = [
        'user_id', 'first_name', 'last_name', 'middle_name', 'email'
    ]
    if include_password:
        select_fields.append('password')
    
    # Создаем динамический SQL запрос
    conditions = []
    params = []
    
    # Поддержка всех полей поиска
    for field in ['first_name', 'last_name', 'middle_name', 'email']:
        if field in search_data and search_data[field]:
            conditions.append(f"{field} ILIKE %s")
            params.append(f"%{re.sub('\\s+', ' ', search_data[field].strip())}%")
    
    where_clause = " AND ".join(conditions) if conditions else "TRUE"
    
    query = sql.SQL('''
        SELECT {fields}
        FROM users
        WHERE {where_condition}
        ORDER BY {sort_field}
        LIMIT %s
        OFFSET %s;
    ''').format(
        fields=sql.SQL(', ').join(map(sql.Identifier, select_fields)),
        where_condition=sql.SQL(where_clause),
        sort_field=sql.Identifier(sort_field)
    )
    params.extend([limit, offset])
    
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        
        