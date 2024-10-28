import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt
from sklearn.preprocessing import MultiLabelBinarizer
from pathlib import Path


def preprocess_tags(tags_column):
    # Clean and preprocess the tags, removing special characters and converting them into Python lists.
    return tags_column.apply(lambda x: eval(x))

def create_transaction_matrix(tags_column):
    # Convert the tags into a transaction matrix using one-hot encoding (like a basket of items).
    mlb = MultiLabelBinarizer()
    transaction_matrix = pd.DataFrame(mlb.fit_transform(tags_column), columns=mlb.classes_, index=tags_column.index)
    return transaction_matrix, mlb

def apply_apriori(transaction_matrix, min_support=0.05):
    # Use the Apriori algorithm to find frequent itemsets (tag combinations).
    frequent_itemsets = apriori(transaction_matrix, min_support=min_support, use_colnames=True)
    return frequent_itemsets

def cluster_recipes_by_tags(frequent_itemsets, transaction_matrix, min_common_tags=5):
    # Find frequent tagsets and cluster recipes based on those patterns.
    frequent_tagsets = frequent_itemsets[frequent_itemsets['itemsets'].apply(lambda x: len(x) >= min_common_tags)]
    
    # For each recipe, calculate which frequent tagsets they belong to.
    recipe_clusters = []
    for i, recipe_tags in transaction_matrix.iterrows():
        clusters = []
        for idx, itemset in enumerate(frequent_tagsets['itemsets']):
            if all(tag in recipe_tags[recipe_tags == 1].index for tag in itemset):
                clusters.append(idx)
        recipe_clusters.append(clusters if clusters else [-1])  # Assign -1 if no cluster matches
    
    return recipe_clusters

def run_apriori_clustering(min_support=0.05, min_common_tags=5):
    project_root = Path(__file__).parent.parent.parent
    data_path = project_root / "data"
    # Load the recipes dataset
    recipes_path = data_path / "RAW_recipes/RAW_recipes.csv" 
    recipes = pd.read_csv(recipes_path)

    # Step 1: Preprocess the tags
    recipes['clean_tags'] = preprocess_tags(recipes['tags'])

    # Step 2: Create a transaction matrix for Apriori
    transaction_matrix, mlb = create_transaction_matrix(recipes['clean_tags'])

    # Step 3: Apply Apriori algorithm to find frequent tag patterns
    frequent_itemsets = apply_apriori(transaction_matrix, min_support=min_support)

    # Step 4: Cluster recipes based on common tag patterns
    recipe_clusters = cluster_recipes_by_tags(frequent_itemsets, transaction_matrix, min_common_tags)

    # Step 5: Add cluster labels to the dataframe
    recipes['cluster'] = [','.join(map(str, cluster)) for cluster in recipe_clusters]
    
    # Return the clustered recipes
    return recipes[['name', 'tags', 'cluster']]

if __name__ == '__main__':
    clustered_recipes = run_apriori_clustering(min_support=0.05, min_common_tags=5)
    print(clustered_recipes.head())
