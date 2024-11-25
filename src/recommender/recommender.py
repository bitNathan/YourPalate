import joblib
import pandas as pd
import json
import random
import time
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from src.db import create_connection


def load_user_ratings():
    """
    Load user ratings from the `user_ratings` table.

    """
    conn = create_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT recipe_id, user_ratings FROM `User-restrictions`.`user_ratings`;")
        ratings_data = cursor.fetchall()
        ratings = pd.DataFrame(ratings_data)
        ratings['user_ratings'] = ratings['user_ratings'].apply(json.loads)  # Convert JSON strings to dicts
    finally:
        cursor.close()
        conn.close()

    return ratings


def create_user_matrix(ratings, expected_features=None):
    """
    Create a user matrix from the database-sourced ratings data.
    """
    user_data = []
    for _, row in ratings.iterrows():
        recipe_id = row['recipe_id']
        for user_id, rating in row['user_ratings'].items():
            user_data.append((user_id, recipe_id, rating))
    user_matrix_df = pd.DataFrame(user_data, columns=['user_id', 'recipe_id', 'rating'])

    user_matrix = user_matrix_df.pivot(index='user_id', columns='recipe_id', values='rating').fillna(0)

    if expected_features is not None:
        missing_features = list(set(expected_features) - set(user_matrix.columns))
        missing_columns = pd.DataFrame(0, index=user_matrix.index, columns=missing_features)
        user_matrix = pd.concat([user_matrix, missing_columns], axis=1)
        user_matrix = user_matrix[expected_features]

    return user_matrix


def get_similar_users(knn, user_matrix, user_id, n_neighbors=10):
    """
    Find similar users using KNN.
    """
    if str(user_id) not in user_matrix.index:
        raise ValueError(f"User ID {user_id} not found in user ratings.")

    user_vector = user_matrix.loc[[str(user_id)]]
    distances, indices = knn.kneighbors(user_vector, n_neighbors=n_neighbors)
    similar_user_ids = [user_matrix.index[i] for i in indices[0]]
    return similar_user_ids


def get_top_recipes_from_similar_users(ratings, similar_user_ids, n=100):
    """
    Aggregate ratings from similar users and find the top recipes.
    """
    recipe_scores = {}
    for _, row in ratings.iterrows():
        user_ratings = row['user_ratings']
        for user_id in similar_user_ids:
            if str(user_id) in user_ratings:
                recipe_scores[row['recipe_id']] = recipe_scores.get(row['recipe_id'], 0) + user_ratings[str(user_id)]

    top_recipes = sorted(recipe_scores.items(), key=lambda x: x[1], reverse=True)[:n]
    recommended_recipes = [recipe for recipe, _ in top_recipes]
    random.shuffle(recommended_recipes)

    return recommended_recipes


def get_recipe_details(recipe_ids):
    """
    Fetch recipe details for given recipe IDs from the `filtered_recipes_clustered` table.
    """
    conn = create_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        placeholders = ", ".join(["%s"] * len(recipe_ids))
        query = f"""
            SELECT * FROM `User-restrictions`.`filtered_recipes_clustered`
            WHERE id IN ({placeholders});
        """
        cursor.execute(query, recipe_ids)
        recipes = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return recipes


def run(user_id=23333, n_neighbors=10):
    """
    Main function to run the recommender system.
    """
    # print("Loading user ratings...")
    ratings = load_user_ratings()

    # print("Loading KNN model...")
    knn = joblib.load('knn_larger_subset_model_n100.joblib')

    # print("Creating user matrix...")
    expected_features = knn.get_feature_names_out() if hasattr(knn, 'get_feature_names_out') else knn.feature_names_in_
    user_matrix = create_user_matrix(ratings, expected_features)

    # print("Finding similar users...")
    similar_user_ids = get_similar_users(knn, user_matrix, user_id, n_neighbors)
    print("Similar users:", similar_user_ids)

    # print("Generating recommendations...")
    recommended_recipe_ids = get_top_recipes_from_similar_users(ratings, similar_user_ids)

    # print("Fetching recipe details...")
    recipe_details = get_recipe_details(recommended_recipe_ids)

    recommended_recipes = [f"{recipe['name']} (ID: {recipe['id']})" for recipe in recipe_details]
    recommendations_list = ", ".join(recommended_recipes)

    # TODO
    # Display the recommendations names, ingredients, discriptions via SQL

    # TODO
    # make shopping list file via SQL

    return similar_user_ids, recommendations_list


if __name__ == '__main__':
    start_time = time.time()
    print("Running the recommender...")
    similar_users, recommendations = run(user_id=23333)
    print("Recommendations generated in %s seconds" % (time.time() - start_time))
    print("Similar users:", similar_users)
    print("Recommended recipes:", recommendations)
