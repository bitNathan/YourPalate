import joblib
import pandas as pd
import random
import time
import json
import sys
from pathlib import Path
from sqlalchemy import create_engine
from collections import Counter


project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.db import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT


def load_recipe_ratings():
    db_url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(db_url)

    query = "SELECT recipe_id, user_ratings FROM user_ratings;"
    df = pd.read_sql(query, engine)
    # print(df.shape)

    user_data = []
    for _, row in df.iterrows():
        recipe_id = row["recipe_id"]
        user_ratings = json.loads(row["user_ratings"])
        for user_id, rating in user_ratings.items():
            user_data.append({"user_id": str(user_id), "recipe_id": recipe_id, "rating": rating})

    ratings = pd.DataFrame(user_data)
    # print(ratings.shape)

    return ratings


def create_user_matrix(ratings, expected_features=None):
    user_matrix_df = ratings.pivot(index='user_id', columns='recipe_id', values='rating').fillna(0)
    # print("done making matrix")

    if expected_features is not None:
        missing_features = list(set(expected_features) - set(user_matrix_df.columns))
        missing_columns = pd.DataFrame(0, index=user_matrix_df.index, columns=missing_features)
        user_matrix_df = pd.concat([user_matrix_df, missing_columns], axis=1)
        user_matrix_df = user_matrix_df[expected_features]

    return user_matrix_df


def get_similar_users(knn, user_matrix, user_id, n_neighbors=5):
    if str(user_id) not in user_matrix.index:
        raise ValueError(f"User ID {user_id} not found in user ratings.")

    user_vector = user_matrix.loc[[str(user_id)]]

    distances, indices = knn.kneighbors(user_vector, n_neighbors=n_neighbors)
    similar_user_ids = [user_matrix.index[i] for i in indices[0]]
    return similar_user_ids


def get_top_recipes_from_similar_users(ratings, similar_user_ids, n=100):
    recipe_scores = {}

    for _, row in ratings.iterrows():
        if row['user_id'] in similar_user_ids:
            recipe_scores[row['recipe_id']] = recipe_scores.get(row['recipe_id'], 0) + row['rating']

    top_recipes = sorted(recipe_scores.items(), key=lambda x: x[1], reverse=True)[:n]
    recommended_recipes = [recipe for recipe, _ in top_recipes]

    random.shuffle(recommended_recipes)

    return recommended_recipes


def fetch_valid_recipes(engine, recipe_ids):
    recipe_ids_str = ', '.join(map(str, recipe_ids))

    query = f"""
        SELECT id, name, Ingredient_amounts, description
        FROM recipes
        WHERE id IN ({recipe_ids_str});
    """
    return pd.read_sql(query, engine)


def clean_ingredient(ingredient):
    """Cleans up an ingredient string by removing brackets and quotes."""
    return ingredient.strip("[]'\"").strip()


def generate_shopping_list(recipe_details):
    """Create a shopping list file based on the ingredients of recommended recipes."""
    shopping_list = []

    for i in recipe_details["Ingredient_amounts"]:
        cleaned_i = clean_ingredient(i)
        shopping_list.append(cleaned_i)

    grouped_ingredients = Counter(shopping_list)

    presentable_list = []
    for ingredient, count in grouped_ingredients.items():
        if count > 1:
            presentable_list.append(f"{count} x {ingredient}")
        else:
            presentable_list.append(ingredient)

    presentable_list.sort()
    return presentable_list


def run(user_id=23333, n_neighbors=100):
    project_root = Path(__file__).parent.parent.parent

    # print("Loading recipe ratings...")
    ratings = load_recipe_ratings()

    # print("Loading KNN model...")
    knn = joblib.load(project_root / 'src/recommender/knn_larger_subset_model_n100.joblib')

    # print("getting features")
    expected_features = knn.get_feature_names_out() if hasattr(knn, 'get_feature_names_out') else knn.feature_names_in_

    # print("Creating user matrix...")
    user_matrix = create_user_matrix(ratings, expected_features)

    # print("Finding similar users...")
    similar_user_ids = get_similar_users(knn, user_matrix, user_id, n_neighbors)
    # print("Similar users:", similar_user_ids)

    # print("Generating recommendations...")
    recommended_recipe_ids = get_top_recipes_from_similar_users(ratings, similar_user_ids)

    # recommendations_list = ", ".join(map(str, recommended_recipe_ids))
    # print(f"Recommendations for user {user_id}: {recommendations_list}")

    # print("Fetching recipe details...")
    # Initialize the database connection
    db_url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(db_url)

    # Fetch details for all recommended recipes
    all_recipe_details_df = fetch_valid_recipes(engine, recommended_recipe_ids)

    all_recipe_details_df = all_recipe_details_df.sample(frac=1, random_state=42).reset_index(drop=True)

    first_21 = all_recipe_details_df[:21]

    recommendations = (
        first_21[['name', 'description']]
        .dropna()  # Remove rows with missing values for 'name' or 'description'
        .to_dict(orient='records')  # Convert to a list of dictionaries
    )

    # print("All recipe details:", all_recipe_details_df)

    # print("Generating shopping list...")
    # shopping_list = generate_shopping_list(all_recipe_details_df)
    shopping_list = generate_shopping_list(first_21[first_21['id'].isin(recommended_recipe_ids)])

    # print("Recommendations fetched successfully.")

    return similar_user_ids, recommendations, shopping_list


if __name__ == '__main__':
    start_time = time.time()
    print("Running the recommender...")
    similar_users, recommendations, shopping_list = run(user_id=23333)
    print("Recommendations generated in %s seconds" % (time.time() - start_time))
    print("Similar users:", similar_users)
    print("Recommended recipes:", recommendations)
    print("Shopping list:", shopping_list)
