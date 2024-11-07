import pandas as pd
import json
from pathlib import Path


def dict_ratings():
    project_root = Path(__file__).parent.parent.parent
    data_path = project_root / "data"

    # Load the original reviews CSV
    reviews_df = pd.read_csv(data_path / "filtered_user_interactions.csv")

    # Group by recipe_id and create a dictionary of user ratings
    optimized_data = reviews_df.groupby('recipe_id').apply(
        lambda x: x.set_index('user_id')['rating'].to_dict()
    ).reset_index(name='user_ratings')

    # Convert user ratings to JSON strings for efficient storage in CSV
    optimized_data['user_ratings'] = optimized_data['user_ratings'].apply(json.dumps)

    # Save to a new CSV file
    optimized_data.to_csv(data_path / "user_ratings.csv", index=False)

    return optimized_data


if __name__ == '__main__':
    data = dict_ratings()
    print(data.head())
    print(len(data))
