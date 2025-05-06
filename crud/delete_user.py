def delete_user(connection, user_id: int) -> int:
    """Удаляет пользователя по ID и возвращает количество удаленных записей"""
    cursor = connection.cursor()
    query = '''
        DELETE FROM users
        WHERE user_id = %s;
    '''
    try:
        cursor.execute(query, (user_id,))
        result = cursor.rowcount
        connection.commit()
        return result
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()


def delete_users_many(connection, user_ids: tuple) -> int:
    """Удаляет нескольких пользователей и возвращает количество удаленных записей"""
    if not user_ids:
        return 0
    
    cursor = connection.cursor()
    query = '''
        DELETE FROM users
        WHERE user_id IN %s;
    '''
    try:
        cursor.execute(query, (user_ids,))
        result = cursor.rowcount
        connection.commit()
        return result
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()