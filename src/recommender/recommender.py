import joblib
import pandas as pd

recipes = pd.read_csv('data/RAW_recipes.csv')
data = pd.read_csv('data/user_recipe_matrix_subset.csv')
data.set_index(data.columns[0], inplace=True)

knn = joblib.load('src/recommender/knn_subset_model.joblib')


def get_n_recommendations(data, indices, n=10):
    similar_users = data.iloc[indices[0]]
    recipe_sums = similar_users.sum(axis=0)
    top_recipes = recipe_sums.sort_values(ascending=False)[:n]
    top_recipes_indices = top_recipes.index.values.astype(int)
    recommendations = recipes[recipes['id'].isin(top_recipes_indices)]

    return recommendations


def get_similar_users(knn, datapoint):
    distances, indices = knn.kneighbors([datapoint])
    return indices


if __name__ == '__main__':
    user_id = 0
    datapoint = data.iloc[user_id]
    indices = get_similar_users(knn, datapoint)
    recommendations = get_n_recommendations(data, indices)
    # print(recommendations)
