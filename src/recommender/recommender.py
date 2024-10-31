import joblib
import pandas as pd
from pathlib import Path
import time

# from web_design.sample_site import 


def get_n_recommendations(data, indices, recipes, n=10):
    similar_users = data.iloc[indices[0]]
    recipe_sums = similar_users.sum(axis=0)
    top_recipes = recipe_sums.sort_values(ascending=False)[:n]
    top_recipes_indices = top_recipes.index.values.astype(int)
    recommendations = recipes[recipes['id'].isin(top_recipes_indices)]

    return recommendations


def get_similar_users(knn, datapoint, features):
    datapoint_dense = pd.DataFrame([datapoint.sparse.to_dense().values], columns=features)
    _, indices = knn.kneighbors(datapoint_dense)
    return indices


def run(user_id=1):
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    data_path = project_root / "data"

    print("here")
    
    recipes = pd.read_csv(data_path / "RAW_recipes/RAW_recipes.csv")
    
    print("here2")
    
    data = pd.read_csv(data_path / 'user_recipe_matrix_subset/user_recipe_matrix_subset.csv')
    
    print("here3")
    sparse_df = data.astype(pd.SparseDtype("int", 0))
    print("here4")

    # sparse_df.to_csv(data_path / 'sparse_user_recipe_matrix.csv')
    print("here5")

    sparse_df.set_index(sparse_df.columns[0], inplace=True)
    print("here6")

    knn = joblib.load(project_root / 'src/recommender/knn_subset_model.joblib')
    print("here7")

    feature_columns = sparse_df.columns
    
    datapoint = sparse_df.iloc[user_id]
    print("here8")

    indices = get_similar_users(knn, datapoint, feature_columns)
    print("here9")

    recommendations = get_n_recommendations(sparse_df, indices, recipes)
    print("here10")

    # TODO recommendations.name.values isn't comma seperated
    #   could be fixed here or in views.py but needed for good display
    return recommendations


if __name__ == '__main__':
    start_time = time.time()
    print("Running the recommender...")
    recommendations = run()
    print("Recommendations generated in %s seconds" % (time.time() - start_time))
    print(recommendations)
