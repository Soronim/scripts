from crud.retrieve_user import user_exists_by_email,user_exists_by_id
import psycopg2
import re
from crud.create_user import validate_name, validate_password,capitalize_name,validate_email

# Define a separate function for the actual database update
def _perform_db_update_user(connection, user_id: int, user_data: dict) -> bool:
    """Performs the actual database update for a user."""
    try:
        cursor = connection.cursor()
        
        # Build the SET clause dynamically based on the provided user_data
        set_clauses = []
        values = []
        
        if 'last_name' in user_data:
            set_clauses.append("last_name = %s")
            values.append(user_data['last_name'])
            
        if 'first_name' in user_data:
            set_clauses.append("first_name = %s")
            values.append(user_data['first_name'])
            
        if 'middle_name' in user_data:
            set_clauses.append("middle_name = %s")
            values.append(user_data['middle_name'])
            
        if 'email' in user_data:
            set_clauses.append("email = %s")
            values.append(user_data['email'])
            
        if 'password' in user_data:
            # Note: You should hash passwords before storing them in a real application
            set_clauses.append("password = %s")
            values.append(user_data['password'])

        if not set_clauses:
            return False # No data to update

        query = f"""
            UPDATE users
            SET {', '.join(set_clauses)}
            WHERE user_id = %s
        """
        values.append(user_id)

        cursor.execute(query, tuple(values))
        connection.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        return rows_affected > 0
    except psycopg2.Error as e:
        connection.rollback()
        print(f"Database error during update: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during update: {e}")
        return False


def db_update_user(connection) -> None:
    """Процесс обновления данных пользователя с валидацией всех полей"""
    print("\nОбновление данных пользователя")

    # Получаем ID пользователя для обновления
    try:
        user_id = int(input('Введите ID пользователя для изменения: '))
    except ValueError:
        print('Ошибка: ID должен быть числом')
        return

    # Проверяем существование пользователя
    if not user_exists_by_id(connection, user_id):
        print(f'Пользователь с ID {user_id} не найден')
        return

    # Получаем текущие данные пользователя
    cursor = connection.cursor()
    cursor.execute("""
        SELECT first_name, last_name, middle_name, email
        FROM users WHERE user_id = %s
    """, (user_id,))
    current_data = cursor.fetchone()
    cursor.close()

    if not current_data:
        print(f'Ошибка: данные пользователя с ID {user_id} не найдены')
        return

    current_first, current_last, current_middle, current_email = current_data

    print('\nВведите новые данные (оставьте пустым, чтобы оставить текущее значение)')
    print(f'Текущая фамилия: {current_last}')
    last_name = get_optional_input("Новая фамилия: ", validate_name, "фамилия") or current_last

    print(f'Текущее имя: {current_first}')
    first_name = get_optional_input("Новое имя: ", validate_name, "имя") or current_first

    print(f'Текущее отчество: {current_middle if current_middle else "не указано"}')
    middle_name = get_middle_name_input(current_middle)

    print(f'Текущий email: {current_email}')
    email = get_email_input(connection, current_email)

    password = get_optional_input(
        "Новый пароль (оставьте пустым, чтобы не менять): ",
        validate_password
    )

    # Prepare the data for the update function
    user_data_to_update = {}

    if last_name != current_last:
        user_data_to_update['last_name'] = capitalize_name(last_name)

    if first_name != current_first:
        user_data_to_update['first_name'] = capitalize_name(first_name)

    # Handle middle name: if it's the same as current and not None, don't update. If it's different, include it.
    # If current_middle is None and new middle_name is empty, don't update.
    if middle_name != current_middle:
         user_data_to_update['middle_name'] = capitalize_name(middle_name) if middle_name else None


    if email.lower() != current_email.lower():
         user_data_to_update['email'] = email.lower()

    if password: # Only include password if a new one was provided
        user_data_to_update['password'] = password # Remember to hash this!

    # Call the separate function to perform the database update
    if user_data_to_update:
        try:
            updated = _perform_db_update_user(connection, user_id, user_data_to_update)
            if updated:
                print(f"\nДанные пользователя с ID {user_id} успешно обновлены")
                
            else:
                print("\nДанные не были изменены (возможно, не было новых значений)")
        except Exception as e:
            print(f"\nОшибка при обновлении пользователя: {e}")
    else:
        print("\nНет данных для обновления.")


def get_optional_input(prompt: str, validator: callable, *args) -> str:
    """Получает необязательный ввод с валидацией"""
    while True:
        value = input(prompt).strip()
        if not value:
            return ""  # Пустая строка означает оставить текущее значение
        if validator(value, *args):
            return value

def get_middle_name_input(current_middle: str) -> str:
    """Специальная обработка для отчества (можно удалить)"""
    while True:
        value = input("Новое отчество (введите '-' чтобы удалить, оставьте пустым чтобы оставить текущее): ").strip()
        if not value:
            return current_middle if current_middle is not None else "" # Return current value
        if value == '-':
            return ""  # Empty string means remove (set to NULL in DB)
        if validate_name(value, "отчество", False):
            return value

def get_email_input(connection, current_email: str) -> str:
    """Специальная обработка для email с проверкой уникальности"""
    while True:
        value = input("Новый email: ").strip()
        if not value:
            return current_email

        if not validate_email(value):
            continue

        if value.lower() == current_email.lower():
            return current_email

        if user_exists_by_email(connection, value):
            print('Ошибка: пользователь с таким email уже существует')
            continue

        return value

