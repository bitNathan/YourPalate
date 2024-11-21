import joblib
import pandas as pd
from pathlib import Path
import time
import json


def load_recipe_ratings():
    project_root = Path(__file__).parent.parent.parent
    data_path = project_root / "data"
    optimized_ratings_path = data_path / "user_ratings.csv"

    # Load optimized ratings and convert JSON strings back to dictionaries
    ratings = pd.read_csv(optimized_ratings_path)
    ratings['user_ratings'] = ratings['user_ratings'].apply(json.loads)
    return ratings


def create_user_matrix(ratings, expected_features=None):
    # Expand user ratings into a sparse user matrix format
    user_data = []
    for _, row in ratings.iterrows():
        recipe_id = row['recipe_id']
        for user_id, rating in row['user_ratings'].items():
            user_data.append((user_id, recipe_id, rating))
    user_matrix_df = pd.DataFrame(user_data, columns=['user_id', 'recipe_id', 'rating'])
    user_matrix = user_matrix_df.pivot(index='user_id', columns='recipe_id', values='rating').fillna(0)

    # If expected features (recipes) are provided, align the matrix columns
    if expected_features is not None:
        missing_features = list(set(expected_features) - set(user_matrix.columns))  # Convert set to list
        # if missing_features:
        # Add missing features as columns with 0 ratings in a single operation
        missing_columns = pd.DataFrame(0, index=user_matrix.index, columns=missing_features)
        user_matrix = pd.concat([user_matrix, missing_columns], axis=1)

        # Reorder columns to match expected features
        user_matrix = user_matrix[expected_features]

    return user_matrix


def get_similar_users(knn, user_matrix, user_id, n_neighbors=5):
    # Ensure the user_id exists in the matrix
    if str(user_id) not in user_matrix.index:
        raise ValueError(f"User ID {user_id} not found in user ratings.")

    # Get the user's ratings vector
    user_vector = user_matrix.loc[[str(user_id)]]

    # Find similar users
    distances, indices = knn.kneighbors(user_vector, n_neighbors=n_neighbors)
    similar_user_ids = [user_matrix.index[i] for i in indices[0]]
    return similar_user_ids


def get_top_recipes_from_similar_users(ratings, similar_user_ids, n=10):
    # Aggregate ratings from similar users and find the top recipes
    recipe_scores = {}

    for _, row in ratings.iterrows():
        user_ratings = row['user_ratings']

        # Sum ratings of similar users for each recipe
        for user_id in similar_user_ids:
            if str(user_id) in user_ratings:
                recipe_scores[row['recipe_id']] = recipe_scores.get(row['recipe_id'], 0) + user_ratings[str(user_id)]

    # Sort recipes by aggregated score and get the top N
    top_recipes = sorted(recipe_scores.items(), key=lambda x: x[1], reverse=True)[:n]
    recommended_recipes = [recipe for recipe, _ in top_recipes]

    return recommended_recipes


def run(user_id=23333, n_neighbors=5):
    project_root = Path(__file__).parent.parent.parent

    # Load optimized recipe ratings
    print("Loading optimized recipe ratings...")
    ratings = load_recipe_ratings()

    # Load the KNN model
    print("Loading KNN model...")
    knn = joblib.load(project_root / 'src/recommender/knn_subset_model.joblib')

    # Retrieve expected features from the KNN model and create user matrix
    print("Creating user matrix...")
    expected_features = knn.get_feature_names_out() if hasattr(knn, 'get_feature_names_out') else knn.feature_names_in_
    user_matrix = create_user_matrix(ratings, expected_features)

    # Find similar users
    print("Finding similar users...")
    similar_user_ids = get_similar_users(knn, user_matrix, user_id, n_neighbors)
    print("Similar users:", similar_user_ids)

    # Generate recommendations based on similar users
    print("Generating recommendations...")
    recommendations = get_top_recipes_from_similar_users(ratings, similar_user_ids)

    # Convert recommendation list to comma-separated format for display
    recommendations_list = ", ".join(map(str, recommendations))

    return similar_user_ids, recommendations_list


if __name__ == '__main__':
    start_time = time.time()
    print("Running the recommender...")
    similar_users, recommendations = run(user_id=23333)
    print("Recommendations generated in %s seconds" % (time.time() - start_time))
    print("Similar users:", similar_users)
    print("Recommended recipes:", recommendations)
