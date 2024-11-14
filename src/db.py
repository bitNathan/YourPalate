import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_PORT = int(os.getenv('DB_PORT', 3306))

def create_server_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

def create_database():
    conn = create_server_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`;")
        print(f"Database '{DB_NAME}' created")
    finally:
        cursor.close()
        conn.close()

def create_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

def initialize_database():
    create_database()

    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_restrictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                vegetarian BOOLEAN NOT NULL,
                calories INT NOT NULL,
                max_time INT NOT NULL
            );
        """)
        conn.commit()
        print("Table 'users_restrictions' created")
    finally:
        cursor.close()
        conn.close()

def add_user(vegetarian, calories, max_time):
    conn = create_connection()
    user_id = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users_restrictions (vegetarian, calories, max_time)
            VALUES (%s, %s, %s);
        """, (vegetarian, calories, max_time))
        conn.commit()
        user_id = cursor.lastrowid
        print(f"User added with ID: {user_id}")
    finally:
        cursor.close()
        conn.close()
    return user_id

def get_user(user_id):
    conn = create_connection()
    user_data = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM users_restrictions WHERE id = %s;
        """, (user_id,))
        user_data = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
    return user_data

def update_user(user_id, vegetarian=None, calories=None, max_time=None):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        updates = []
        values = []

        if vegetarian is not None:
            updates.append("vegetarian = %s")
            values.append(vegetarian)
        if calories is not None:
            updates.append("calories = %s")
            values.append(calories)
        if max_time is not None:
            updates.append("max_time = %s")
            values.append(max_time)

        values.append(user_id)
        update_clause = ", ".join(updates)

        cursor.execute(f"""
            UPDATE users_restrictions
            SET {update_clause}
            WHERE id = %s;
        """, values)
        conn.commit()

        if cursor.rowcount > 0:
            print(f"User with ID {user_id} updated.")
            return 1
        else:
            print(f"No user found with ID: {user_id}.")
            return 0
    finally:
        cursor.close()
        conn.close()

def delete_user(user_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM users_restrictions WHERE id = %s;
        """, (user_id,))
        conn.commit()

        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()

def test_database_functions():
    print("\n--- Initializing Database ---")
    initialize_database()

    # Test adding a new user
    print("\n--- Adding a New User ---")
    user_id = add_user(vegetarian=True, calories=1500, max_time=30)
    print(f"Added user with ID: {user_id}")

    # Test retrieving the user
    print("\n--- Retrieving the User ---")
    user_data = get_user(user_id)
    if user_data:
        print("Retrieved user data:", user_data)
    else:
        print("User not found.")

    # Test retrieving a non-existent user
    print("\n--- Retrieving a Non-Existent User ---")
    non_existent_user_data = get_user(9999)
    if non_existent_user_data:
        print("Retrieved data for non-existent user:", non_existent_user_data)
    else:
        print("No data found for non-existent user.")

    # Test updating the user
    print("\n--- Updating the User ---")
    update_result = update_user(user_id, vegetarian=False, calories=1200)
    if update_result:
        print("User updated successfully.")
    else:
        print("Failed to update user.")

    # Test updating a non-existent user
    print("\n--- Updating a Non-Existent User ---")
    non_existent_update_result = update_user(9999, vegetarian=True)
    if non_existent_update_result:
        print("Non-existent user updated successfully.")
    else:
        print("Failed to update non-existent user.")

    # Test deleting the user
    print("\n--- Deleting the User ---")
    delete_result = delete_user(user_id)
    if delete_result:
        print("User deleted successfully.")
    else:
        print("Failed to delete user.")

    # Test deleting a non-existent user
    print("\n--- Deleting a Non-Existent User ---")
    non_existent_delete_result = delete_user(9999)
    if non_existent_delete_result:
        print("Non-existent user deleted successfully.")
    else:
        print("Failed to delete non-existent user.")


# test_database_functions()