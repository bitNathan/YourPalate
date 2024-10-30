import pandas as pd
from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt
from sklearn.preprocessing import MultiLabelBinarizer
from pathlib import Path
from apriori import apriori
from itertools import combinations


def preprocess_tags(tags_column):
    # Clean and preprocess the tags, removing special characters and converting them into Python lists.
    return tags_column.apply(lambda x: eval(x))

def create_transaction_matrix(tags_column):
    # Convert the tags into a transaction matrix using one-hot encoding (like a basket of items).
    mlb = MultiLabelBinarizer()
    transaction_matrix = pd.DataFrame(mlb.fit_transform(tags_column), columns=mlb.classes_, index=tags_column.index)
    return transaction_matrix, mlb

def apply_apriori(transaction_matrix, min_support=0.05):
    # Convert transaction matrix to a list of sets for compatibility with the custom Apriori function
    dataset = [set(transaction_matrix.columns[transaction_matrix.iloc[i].values == 1]) for i in range(len(transaction_matrix))]
    
    # Use the custom Apriori function to find frequent itemsets
    five_item_frequent_sets, support_data = apriori(dataset, min_support=min_support, verbose=False)
    
    frequent_itemsets_df = pd.DataFrame({
        'itemsets': five_item_frequent_sets,
        'support': [support_data[itemset] for itemset in five_item_frequent_sets]
    })
     
    return frequent_itemsets_df


def cluster_recipes_by_tags(frequent_itemsets, transaction_matrix, min_common_tags=5):
    # Find frequent tagsets and cluster recipes based on those patterns.
    frequent_tagsets = [set(itemset) for itemset in frequent_itemsets['itemsets'] if len(itemset) == min_common_tags]
    
    # For each recipe, calculate which frequent tagsets they belong to.
    recipe_clusters = []
    for i, recipe_tags in transaction_matrix.iterrows():
        # Convert active tags in the recipe to a set
        active_tags = set(recipe_tags[recipe_tags == 1].index)
        
        # Find matching clusters for the recipe based on frequent 5-tag sets
        clusters = [idx for idx, itemset in enumerate(frequent_tagsets) if itemset.issubset(active_tags)]
        
        # Append cluster indices or [-1] if no matches found
        recipe_clusters.append(clusters if clusters else [-1])
        
    return recipe_clusters

def run_apriori_clustering(min_support=0.05, min_common_tags=5):
    project_root = Path(__file__).parent.parent.parent
    data_path = project_root / "data"
    # Load the recipes dataset
    recipes_path = data_path / "RAW_recipes/RAW_recipes.csv" 
    recipes = pd.read_csv(recipes_path)
    print("Data loaded.")
    
    # Step 1: Preprocess the tags
    recipes['clean_tags'] = preprocess_tags(recipes['tags'])
    print("Tags preprocessed.")

    # Step 2: Create a transaction matrix for Apriori
    transaction_matrix, mlb = create_transaction_matrix(recipes['clean_tags'])
    print("Transaction matrix created.")

    # Step 3: Apply Apriori algorithm to find frequent tag patterns
    frequent_itemsets = apply_apriori(transaction_matrix, min_support=min_support)
    print("Frequent itemsets found.")
    
    # Step 4: Cluster recipes based on common tag patterns
    recipe_clusters = cluster_recipes_by_tags(frequent_itemsets, transaction_matrix, min_common_tags)
    print("Recipes clustered.")
    
    # Step 5: Add cluster labels to the dataframe
    recipes['cluster'] = [','.join(map(str, cluster)) for cluster in recipe_clusters]
    print("Clusters added to DataFrame.")
    
    # Return the clustered recipes
    return recipes[['name', 'tags', 'cluster']]

if __name__ == '__main__':
    clustered_recipes = run_apriori_clustering(min_support=0.05, min_common_tags=5)
    print(clustered_recipes.head())
