import pandas as pd
import random


def filter_recipes(recipes, is_vegetarian=None, max_calories=None, max_time=None):
    max_calories = max_calories if max_calories is not None else float('inf')
    max_time = max_time if max_time is not None else float('inf')

    return [
        recipe for recipe in recipes
        if (is_vegetarian is None or recipe.get('vegetarian') == is_vegetarian)
        and recipe.get('calories', 0) <= max_calories
        and recipe.get('time', 0) <= max_time
    ]


def group_recipes(recipes, group_by_column="cluster"):
    grouped = pd.DataFrame(recipes).groupby(group_by_column)
    grouped_dict = {group: data.to_dict(orient="records") for group, data in grouped}

    return grouped_dict


def get_random_recipes_from_groups(groups, num_recipes=5):
    selected_recipes = []
    for recipes in groups.values():
        selected_recipes.extend(random.sample(recipes, min(len(recipes), num_recipes)))
    return selected_recipes


def get_recipes_for_review(groups, group_weights=None, num_recipes=20):
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
    # Initialize a dictionary to store the user's recipe ratings
    user_ratings = {} if user_ratings is None else user_ratings

    # Track likes and dislikes per group
    for group, recipes in selected_recipes['selected_recipes_per_group'].items():
        # Since recipes are IDs directly, we can check against the likes and dislikes lists
        group_likes = sum(1 for recipe_id in recipes if recipe_id in likes)
        group_dislikes = sum(1 for recipe_id in recipes if recipe_id in dislikes)

        # Update weights based on feedback
        group_weights[group] *= (like_weight ** group_likes) * (dislike_weight ** group_dislikes)

        # Add user ratings for each recipe based on the feedback lists
        for recipe_id in recipes:
            if recipe_id in likes:
                user_ratings[recipe_id] = 5  # Liked recipes get a rating of 5
            elif recipe_id in dislikes:
                user_ratings[recipe_id] = 1  # Disliked recipes get a rating of 1
            else:
                user_ratings[recipe_id] = 0  # Neutral or not rated recipes get a rating of 0

    # Normalize weights so they remain relative
    total_weight = sum(group_weights.values())
    group_weights = {group: weight / total_weight for group, weight in group_weights.items()}

    return group_weights, user_ratings


if __name__ == "__main__":
    # Example usage
    recipes = pd.read_csv("../../../data/filtered_recipes_clustered.csv")
    [["name", "id", "cluster", "description"]].to_dict(orient="records")

    groups = group_recipes(recipes, "cluster")
    group_weights = {group: 1.0 for group in groups.keys()}
    print("Initial group weights:")
    print(group_weights)

    # returns a dictionary of two dictionaries
    selected_recipes = get_recipes_for_review(groups, group_weights=group_weights, num_recipes=10)

    print("\nSelected recipes by group")
    # dictionary 1: {group: [recipe_ids]}
    print(selected_recipes["selected_recipes_per_group"])
    print("\nAll selected recipes")
    # dictionary 2: [{id, name}], list of dictionaries, these values can be shown to the user
    print(selected_recipes["all_selected_recipes"])

    for recipe in selected_recipes['all_selected_recipes']:  # prints the recipe id and name
        print(f"ID: {recipe['id']}, Name: {recipe['name']}")

    # creates a list of recipe ids
    selected_recipe_ids = [recipe['id'] for recipe in selected_recipes['all_selected_recipes']]
    likes = random.sample(selected_recipe_ids, k=3)  # Randomly select 3 liked recipes
    remaining_ids = [recipe_id for recipe_id in selected_recipe_ids if recipe_id not in likes]  # Get remaining IDs
    dislikes = random.sample(remaining_ids, k=3)  # Randomly select 3 disliked recipes

    print("\nRandomly selected likes (IDs):", likes)
    print("Randomly selected dislikes (IDs):", dislikes)

    group_weights, user_ratings = update_user_preferences(
        group_weights, selected_recipes, likes=likes, dislikes=dislikes)

    print("\nUpdated group weights:")
    print(group_weights)
    print("\nUser recipe ratings:")
    print(user_ratings)  # User ratings is a dictionary of recipe ids and ratings

    print("\n\nSecond iteration:")
    selected_recipes = get_recipes_for_review(groups, group_weights=group_weights, num_recipes=10)
    print(selected_recipes["selected_recipes_per_group"])

    for recipe in selected_recipes['all_selected_recipes']:
        print(f"ID: {recipe['id']}, Name: {recipe['name']}")

    selected_recipe_ids = [recipe['id'] for recipe in selected_recipes['all_selected_recipes']]
    likes = random.sample(selected_recipe_ids, k=3)
    remaining_ids = [recipe_id for recipe_id in selected_recipe_ids if recipe_id not in likes]
    dislikes = random.sample(remaining_ids, k=3)

    print("\nRandomly selected likes (IDs):", likes)
    print("Randomly selected dislikes (IDs):", dislikes)

    # Remember to pass the user_ratings dictionary from the previous iteration
    group_weights, user_ratings = update_user_preferences(
        group_weights, selected_recipes, likes=likes, dislikes=dislikes, user_ratings=user_ratings)

    print("\nUpdated group weights:")
    print(group_weights)
    print("\nUser recipe ratings:")
    print(user_ratings)
