import psycopg2
from config import host, user, password, db_name

def get_db_connection():
    try:
        return psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
    except Exception as e:
        print(f"\nОшибка подключения: {e}")
        return None