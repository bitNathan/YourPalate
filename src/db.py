import mysql.connector
from dotenv import load_dotenv
import os
import json
import pandas as pd

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
        # Create table for user restrictions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_restrictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                vegetarian BOOLEAN NOT NULL,
                calories INT NOT NULL,
                max_time INT NOT NULL
            );
        """)

        # Create new table for new users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS new_users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_ratings JSON NOT NULL
            );
        """)

        conn.commit()
        print("Table 'users_restrictions' created")
        print("Table 'new_users' created")
    finally:
        cursor.close()
        conn.close()


def add_user_restrictions(vegetarian, calories, max_time):
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


def get_user_restrictions(user_id):
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


def update_user_restrictions(user_id, vegetarian=None, calories=None, max_time=None):
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


def delete_user_restrictions(user_id):
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


def add_new_user(user_id = None, user_ratings=None):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        # Convert user_ratings to JSON string, default to empty JSON object if not provided
        user_ratings_json = json.dumps(user_ratings) if user_ratings else '{}'
        cursor.execute("""
            INSERT INTO new_users (id, user_ratings)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE user_ratings = VALUES(user_ratings);
        """, (user_id, user_ratings_json))
        conn.commit()
        if user_id is None:
            user_id = cursor.lastrowid
        print(f"New user added with ID: {user_id}")
    finally:
        cursor.close()
        conn.close()

    return user_id


def update_new_user_ratings(user_id, new_ratings):
    conn = create_connection()
    try:
        # Fetch the current ratings
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_ratings FROM new_users WHERE id = %s;
        """, (user_id,))
        result = cursor.fetchone()

        if result is None:
            print(f"User with ID {user_id} not found.")
            return False

        current_ratings = json.loads(result['user_ratings'])
        current_ratings.update(new_ratings)  # Merge new ratings with current ratings

        # Update the database
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE new_users
            SET user_ratings = %s
            WHERE id = %s;
        """, (json.dumps(current_ratings), user_id))
        conn.commit()
        print(f"User with ID {user_id} updated.")
        return True
    finally:
        cursor.close()
        conn.close()


def get_new_user_ratings(user_id):
    conn = create_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_ratings FROM new_users WHERE id = %s;
        """, (user_id,))
        result = cursor.fetchone()
        if result:
            return json.loads(result['user_ratings'])
    finally:
        cursor.close()
        conn.close()
    return None


def get_recipes_as_dataframe(recipe_ids):
    conn = create_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        # Handle both single recipe_id and list of recipe_ids
        if isinstance(recipe_ids, int):
            recipe_ids = [recipe_ids]

        # Create placeholders for the query
        placeholders = ", ".join(["%s"] * len(recipe_ids))
        query = f"""
            SELECT * FROM filtered_recipes_clustered
            WHERE id IN ({placeholders});
        """

        cursor.execute(query, recipe_ids)
        results = cursor.fetchall()

        # Convert the result (list of dictionaries) into a pandas DataFrame
        df = pd.DataFrame(results)
    finally:
        cursor.close()
        conn.close()

    return df


def get_table_as_dataframe(table_name):
    conn = create_connection()
    try:
        query = f"SELECT * FROM {table_name};"
        df = pd.read_sql(query, conn)
    finally:
        conn.close()

    return df


def test_database_functions():
    print("\n--- Initializing Database ---")
    initialize_database()

    # Test adding a new user
    print("\n--- Adding a New User ---")
    user_id = add_user_restrictions(vegetarian=True, calories=1500, max_time=30)
    print(f"Added user with ID: {user_id}")

    # Test retrieving the user
    print("\n--- Retrieving the User ---")
    user_data = get_user_restrictions(user_id)
    if user_data:
        print("Retrieved user data:", user_data)
    else:
        print("User not found.")

    # Test retrieving a non-existent user
    print("\n--- Retrieving a Non-Existent User ---")
    non_existent_user_data = get_user_restrictions(9999)
    if non_existent_user_data:
        print("Retrieved data for non-existent user:", non_existent_user_data)
    else:
        print("No data found for non-existent user.")

    # Test updating the user
    print("\n--- Updating the User ---")
    update_result = update_user_restrictions(user_id, vegetarian=False, calories=1200)
    if update_result:
        print("User updated successfully.")
    else:
        print("Failed to update user.")

    # Test updating a non-existent user
    print("\n--- Updating a Non-Existent User ---")
    non_existent_update_result = update_user_restrictions(9999, vegetarian=True)
    if non_existent_update_result:
        print("Non-existent user updated successfully.")
    else:
        print("Failed to update non-existent user.")

    # Test deleting the user
    print("\n--- Deleting the User ---")
    delete_result = delete_user_restrictions(user_id)
    if delete_result:
        print("User deleted successfully.")
    else:
        print("Failed to delete user.")

    # Test deleting a non-existent user
    print("\n--- Deleting a Non-Existent User ---")
    non_existent_delete_result = delete_user_restrictions(9999)
    if non_existent_delete_result:
        print("Non-existent user deleted successfully.")
    else:
        print("Failed to delete non-existent user.")


def test_new_user_table_functions():
    print("\n--- Initializing Database for New Users Table ---")
    initialize_database()

    # Test adding a new user with no initial ratings
    print("\n--- Adding a New User with No Initial Ratings ---")
    user_id_no_ratings = add_new_user()
    print(f"Added new user with ID: {user_id_no_ratings}")

    # Test adding a new user with initial ratings
    print("\n--- Adding a New User with Initial Ratings ---")
    initial_ratings = {"39835": 5, "198709": 3, "1060485": 4}  # Example ratings
    user_id = add_new_user(user_ratings=initial_ratings)
    print(f"Added new user with ID: {user_id}")

    # Test retrieving the user ratings
    print("\n--- Retrieving User Ratings ---")
    user_ratings = get_new_user_ratings(user_id)
    if user_ratings:
        print(f"User ratings for ID {user_id}: {user_ratings}")
    else:
        print(f"No data found for user ID {user_id}")

    # Test retrieving a non-existent user ratings
    print("\n--- Retrieving Ratings for Non-Existent User ---")
    non_existent_ratings = get_new_user_ratings(9999)
    if non_existent_ratings:
        print(f"Ratings for non-existent user ID 9999: {non_existent_ratings}")
    else:
        print("No data found for non-existent user ID 9999.")

    # Test updating user ratings
    print("\n--- Updating User Ratings ---")
    new_ratings = {"39835": 4, "198709": 5, "1060485": 3, "136828": 5, "797590": 4, "851190": 3}
    update_success = update_new_user_ratings(user_id, new_ratings)
    if update_success:
        print(f"User ratings updated successfully for ID {user_id}.")
    else:
        print(f"Failed to update ratings for user ID {user_id}.")

    # Check updated ratings
    print("\n--- Retrieving Updated Ratings ---")
    updated_ratings = get_new_user_ratings(user_id)
    if updated_ratings:
        print(f"Updated ratings for user ID {user_id}: {updated_ratings}")
    else:
        print(f"No data found for user ID {user_id}.")

    # Test updating ratings for a non-existent user
    print("\n--- Updating Ratings for Non-Existent User ---")
    non_existent_update = update_new_user_ratings(9999, {"12345": 5})
    if non_existent_update:
        print("Ratings updated successfully for non-existent user ID 9999.")
    else:
        print("Failed to update ratings for non-existent user ID 9999.")


def test_get_recipes_as_dataframe():
    print("\n--- Testing get_recipes_as_dataframe ---")

    # Test with a single recipe_id
    print("\nFetching single recipe with recipe_id = 63986:")
    try:
        single_recipe_df = get_recipes_as_dataframe(63986)
        if not single_recipe_df.empty:
            print(single_recipe_df)
        else:
            print("No recipe found for recipe_id = 63986.")
    except Exception as e:
        print(f"Error fetching single recipe: {e}")

    # Test with multiple recipe_ids
    print("\nFetching multiple recipes with recipe_ids = [63986, 43026, 23933]:")
    try:
        multiple_recipes_df = get_recipes_as_dataframe([63986, 43026, 23933])
        if not multiple_recipes_df.empty:
            print(multiple_recipes_df)
        else:
            print("No recipes found for the provided recipe_ids.")
    except Exception as e:
        print(f"Error fetching multiple recipes: {e}")

    # Test with non-existent recipe_ids
    print("\nFetching non-existent recipe_ids = [999999, 888888]:")
    try:
        no_recipes_df = get_recipes_as_dataframe([999999, 888888])
        if no_recipes_df.empty:
            print("Correctly returned an empty DataFrame for non-existent recipe_ids.")
        else:
            print("Unexpected data returned for non-existent recipe_ids:")
            print(no_recipes_df)
    except Exception as e:
        print(f"Error fetching non-existent recipes: {e}")


# test_new_user_table_functions()
# test_database_functions()
# test_get_recipes_as_dataframe()
