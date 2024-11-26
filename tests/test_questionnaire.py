import sys
from pathlib import Path
import random

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.recommender.questionnaire import (
    update_user_preferences,
    get_recipes_for_review,
    group_recipes,
    load_recipes_from_sql
)


def test_questionnaire():
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


if __name__ == "__main__":
    test_questionnaire()
