from sqlalchemy import create_engine, Column, Integer, String, Boolean, JSON, Table, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import pandas as pd
import os
import json
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_PORT = os.getenv('DB_PORT', '3306')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class UserRestrictions(Base):
    __tablename__ = 'users_restrictions'

    id = Column(Integer, primary_key=True)  # No autoincrement
    vegetarian = Column(Boolean, nullable=False)
    calories = Column(Integer, nullable=False)
    max_time = Column(Integer, nullable=False)


class NewUsers(Base):
    __tablename__ = 'new_users'

    # Foreign key linking to `users_restrictions.id`
    id = Column(Integer, ForeignKey('users_restrictions.id', ondelete="CASCADE"), primary_key=True)
    user_ratings = Column(JSON, nullable=False)


def initialize_database():
    Base.metadata.create_all(engine)
    print("Database and tables created successfully.")


def add_user_restrictions(user_id, vegetarian, calories, max_time):
    try:
        new_user = UserRestrictions(
            id=user_id,  # Use externally generated ID
            vegetarian=vegetarian,
            calories=calories,
            max_time=max_time
        )
        session.add(new_user)
        session.commit()

        return user_id
    except Exception as e:
        session.rollback()
        print(f"Error adding user with ID {user_id}: {e}")
        return None


def get_user_restrictions(user_id):
    user = session.query(UserRestrictions).filter_by(id=user_id).first()
    if user:
        return {
            "id": user.id,
            "vegetarian": user.vegetarian,
            "calories": user.calories,
            "max_time": user.max_time,
        }
    return None


def update_user_restrictions(user_id, vegetarian=None, calories=None, max_time=None):
    user = session.query(UserRestrictions).filter_by(id=user_id).first()
    if user:
        if vegetarian is not None:
            user.vegetarian = vegetarian
        if calories is not None:
            user.calories = calories
        if max_time is not None:
            user.max_time = max_time
        session.commit()

        return True
    print(f"No user found with ID: {user_id}.")
    return False


def delete_user_restrictions(user_id):
    user = session.query(UserRestrictions).filter_by(id=user_id).first()
    if user:
        session.delete(user)
        session.commit()
        return True
    print(f"No user found with ID: {user_id}.")
    return False


def add_new_user(user_id, user_ratings=None):
    try:
        user_ratings = user_ratings or {}  # Default to empty ratings
        new_user = NewUsers(
            id=user_id,
            user_ratings=json.dumps(user_ratings),  # Save as JSON string
        )
        session.add(new_user)
        session.commit()

        return user_id
    except Exception as e:
        session.rollback()
        print(f"Error adding user with ID {user_id} to new_users: {e}")
        return None


def get_new_user_ratings(user_id):
    user = session.query(NewUsers).filter_by(id=user_id).first()
    if user:
        return user.user_ratings
    return None


def update_new_user_ratings(user_id, new_ratings):
    try:
        # Fetch the user by ID
        user = session.query(NewUsers).filter_by(id=user_id).first()

        if not user:
            print(f"No user found with ID: {user_id}.")
            return False

        # Deserialize user ratings if they exist, otherwise start with an empty dictionary
        if user.user_ratings:
            try:
                current_ratings = json.loads(user.user_ratings)  # Convert JSON string to dictionary
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for user ID {user_id}: {e}")
                current_ratings = {}
        else:
            current_ratings = {}

        # Merge new ratings with current ratings
        current_ratings.update(new_ratings)

        # Serialize back to JSON and save to the database
        user.user_ratings = json.dumps(current_ratings)
        session.commit()
        print(f"User ratings updated successfully for ID {user_id}.")
        return True

    except Exception as e:
        print(f"Error updating user ratings for ID {user_id}: {e}")
        session.rollback()
        return False


def get_recipes_as_dataframe(recipe_ids):
    if isinstance(recipe_ids, int):
        recipe_ids = [recipe_ids]

    query = f"""
        SELECT * FROM recipes
        WHERE id IN ({','.join(map(str, recipe_ids))})
    """
    return pd.read_sql(query, engine)


def get_table_as_dataframe(table_name):
    query = f"SELECT * FROM {table_name};"
    return pd.read_sql(query, engine)


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
    print("\nFetching multiple recipes with recipe_ids = [63986, 54100, 90921]:")
    try:
        multiple_recipes_df = get_recipes_as_dataframe([63986, 54100, 90921])
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


def test_add_and_update_users():
    print("\n--- Testing Add and Update for Both Tables ---")

    print("\n--- Initializing Database ---")
    initialize_database()
    
    # Example external user ID
    user_id = 102
    
    # Add user to `users_restrictions`
    print("\n--- Adding User to users_restrictions ---")
    add_success_restrictions = add_user_restrictions(
        user_id=user_id,
        vegetarian=True,
        calories=1800,
        max_time=45
    )
    if add_success_restrictions:
        print(f"User with ID {user_id} added to users_restrictions.")
    else:
        print(f"Failed to add user with ID {user_id} to users_restrictions.")

    # Add user to `new_users`
    print("\n--- Adding User to new_users ---")
    initial_ratings = {"39835": 4, "198709": 3}  # Example ratings
    add_success_new_users = add_new_user(
        user_id=user_id,
        user_ratings=initial_ratings
    )
    if add_success_new_users:
        print(f"User with ID {user_id} added to new_users.")
    else:
        print(f"Failed to add user with ID {user_id} to new_users.")

    # Verify data in both tables using get functions
    print("\n--- Verifying Data in Both Tables ---")
    restrictions = get_user_restrictions(user_id)
    ratings = get_new_user_ratings(user_id)

    print("\nData in users_restrictions:")
    if restrictions:
        print(restrictions)
    else:
        print(f"No restrictions found for user ID {user_id}.")

    print("\nData in new_users:")
    if ratings:
        print(ratings)
    else:
        print(f"No ratings found for user ID {user_id}.")

    # Update user restrictions
    print("\n--- Updating User Restrictions ---")
    update_restrictions_success = update_user_restrictions(
        user_id=user_id,
        vegetarian=False,
        calories=1500
    )
    if update_restrictions_success:
        print(f"User restrictions updated successfully for ID {user_id}.")
    else:
        print(f"Failed to update user restrictions for ID {user_id}.")

    # Update user ratings
    print("\n--- Updating User Ratings ---")
    new_ratings = {"39835": 5, "198709": 4, "1060485": 3}  # New ratings
    update_ratings_success = update_new_user_ratings(user_id, new_ratings)
    if update_ratings_success:
        print(f"User ratings updated successfully for ID {user_id}.")
    else:
        print(f"Failed to update user ratings for ID {user_id}.")

    # Verify updated data using get functions
    print("\n--- Verifying Updated Data ---")
    updated_restrictions = get_user_restrictions(user_id)
    updated_ratings = get_new_user_ratings(user_id)

    print("\nUpdated data in users_restrictions:")
    if updated_restrictions:
        print(updated_restrictions)
    else:
        print(f"No updated restrictions found for user ID {user_id}.")

    print("\nUpdated ratings in new_users:")
    if updated_ratings:
        print(updated_ratings)
    else:
        print(f"No updated ratings found for user ID {user_id}.")


# test_get_recipes_as_dataframe()
# test_add_and_update_users()
