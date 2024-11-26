import pandas as pd
import random
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.db import create_connection


def filter_recipes(recipes, is_vegetarian=None, max_calories=None, max_time=None):
    """
    Filter recipes based on vegetarian preference, maximum calories, and preparation time.
    """
    max_calories = max_calories if max_calories is not None else float('inf')
    max_time = max_time if max_time is not None else float('inf')

    return [
        recipe for recipe in recipes
        if (is_vegetarian is None or recipe.get('vegetarian') == is_vegetarian) and (
            recipe.get('calories', 0) <= max_calories) and (
                recipe.get('time', 0) <= max_time)
    ]


def group_recipes(recipes, group_by_column="cluster"):
    """
    Group recipes by a specified column (e.g., "cluster").
    """
    grouped = pd.DataFrame(recipes).groupby(group_by_column)
    grouped_dict = {group: data.to_dict(orient="records") for group, data in grouped}

    return grouped_dict


def get_random_recipes_from_groups(groups, num_recipes=5):
    """
    Randomly select a specified number of recipes from each group.
    """
    selected_recipes = []
    for recipes in groups.values():
        selected_recipes.extend(random.sample(recipes, min(len(recipes), num_recipes)))
    return selected_recipes


def get_recipes_for_review(groups, group_weights=None, num_recipes=20):
    """
    Select recipes for review based on weighted group probabilities.
    """
    group_weights = {group: 1.0 for group in groups.keys()} if group_weights is None else group_weights

    total_weight = sum(group_weights.values())
    normalized_weights = {group: weight / total_weight for group, weight in group_weights.items()}

    selected_recipes = {group: [] for group in groups}
    all_selected_recipes = []

    for _ in range(num_recipes):
        selected_group = random.choices(
            population=list(groups.keys()),
            weights=[normalized_weights[group] for group in groups.keys()],
            k=1
        )[0]

        if groups[selected_group]:
            recipe = random.choice(groups[selected_group])
            selected_recipes[selected_group].append(recipe['id'])
            all_selected_recipes.append({'id': recipe['id'], 'name': recipe['name'],
                                         'description': recipe['description']})  # Store only ID and name

    return {'selected_recipes_per_group': selected_recipes,
            'all_selected_recipes': all_selected_recipes}


def update_user_preferences(group_weights, selected_recipes, likes, dislikes,
                            like_weight=1.2, dislike_weight=0.8, user_ratings=None):
    """
    Update user preferences and group weights based on feedback.
    """
    user_ratings = {} if user_ratings is None else user_ratings

    for group, recipes in selected_recipes['selected_recipes_per_group'].items():
        group_likes = sum(1 for recipe_id in recipes if recipe_id in likes)
        group_dislikes = sum(1 for recipe_id in recipes if recipe_id in dislikes)

        group_weights[group] *= (like_weight ** group_likes) * (dislike_weight ** group_dislikes)

        for recipe_id in recipes:
            if recipe_id in likes:
                user_ratings[recipe_id] = 5
            elif recipe_id in dislikes:
                user_ratings[recipe_id] = 1
            else:
                user_ratings[recipe_id] = 0

    total_weight = sum(group_weights.values())
    group_weights = {group: weight / total_weight for group, weight in group_weights.items()}

    return group_weights, user_ratings


def load_recipes_from_sql():
    """
    Load recipes from the SQL `filtered_recipes_clustered` table and derive fields like calories, vegetarian, and time.
    """
    conn = create_connection()
    try:
        query = """
        SELECT
            name,
            id,
            cluster,
            description,
            SUBSTRING_INDEX(SUBSTRING_INDEX(nutrition, ',', 1), '[', -1) AS calories,  -- Extract calories
            CASE
                WHEN tags LIKE '%vegetarian%' THEN 1
                ELSE 0
            END AS vegetarian,  -- Determine vegetarian status
            minutes AS time,  -- Use minutes as time
            tags,
            nutrition,
            n_steps,
            steps,
            ingredients,
            n_ingredients,
            ingredients_str
        FROM filtered_recipes_clustered;
        """
        recipes = pd.read_sql(query, conn)
    finally:
        conn.close()

    # Ensure proper data types
    recipes['calories'] = recipes['calories'].astype(float)
    recipes['vegetarian'] = recipes['vegetarian'].astype(bool)
    recipes['time'] = recipes['time'].astype(int)

    return recipes.to_dict(orient="records")


if __name__ == "__main__":
    # Load recipes from SQL table
    recipes = load_recipes_from_sql()

    # Group recipes by "cluster"
    groups = group_recipes(recipes, "cluster")
    group_weights = {group: 1.0 for group in groups.keys()}
    print("Initial group weights:")
    print(group_weights)

    # Select recipes for review
    selected_recipes = get_recipes_for_review(groups, group_weights=group_weights, num_recipes=10)

    print("\nSelected recipes by group")
    print(selected_recipes["selected_recipes_per_group"])
    print("\nAll selected recipes")
    print(selected_recipes["all_selected_recipes"])

    for recipe in selected_recipes['all_selected_recipes']:
        print(f"ID: {recipe['id']}, Name: {recipe['name']}")

    selected_recipe_ids = [recipe['id'] for recipe in selected_recipes['all_selected_recipes']]
    likes = random.sample(selected_recipe_ids, k=3)
    remaining_ids = [recipe_id for recipe_id in selected_recipe_ids if recipe_id not in likes]
    dislikes = random.sample(remaining_ids, k=3)

    print("\nRandomly selected likes (IDs):", likes)
    print("Randomly selected dislikes (IDs):", dislikes)

    group_weights, user_ratings = update_user_preferences(
        group_weights, selected_recipes, likes=likes, dislikes=dislikes)

    print("\nUpdated group weights:")
    print(group_weights)
    print("\nUser recipe ratings:")
    print(user_ratings)
