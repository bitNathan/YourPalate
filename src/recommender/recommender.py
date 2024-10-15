import joblib
import pandas as pd
from pathlib import Path
import time


def get_n_recommendations(data, indices, recipes, n=10):
    similar_users = data.iloc[indices[0]]
    recipe_sums = similar_users.sum(axis=0)
    top_recipes = recipe_sums.sort_values(ascending=False)[:n]
    top_recipes_indices = top_recipes.index.values.astype(int)
    recommendations = recipes[recipes['id'].isin(top_recipes_indices)]

    return recommendations


def get_similar_users(knn, datapoint):
    distances, indices = knn.kneighbors([datapoint])
    return indices


def run(user_id=1):
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    data_path = project_root / "data"

    recipes = pd.read_csv(data_path / "RAW_recipes/RAW_recipes.csv")
    data = pd.read_csv(data_path / 'user_recipe_matrix_subset/user_recipe_matrix_subset.csv')
    data.set_index(data.columns[0], inplace=True)

    knn = joblib.load(project_root / 'src/recommender/knn_subset_model.joblib')

    datapoint = data.iloc[user_id]
    indices = get_similar_users(knn, datapoint)
    recommendations = get_n_recommendations(data, indices, recipes)

    # TODO recommendations.name.values isn't comma seperated
    #   could be fixed here or in views.py but needed for good display
    return recommendations


if __name__ == '__main__':
    start_time = time.time()
    print("Running the recommender...")
    recommendations = run()
    print("Recommendations generated in %s seconds" % (time.time() - start_time))
    print(recommendations)
