import time
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.recommender.recommender import run


def test_recommender():
    start_time = time.time()
    print("Running the recommender...")
    similar_users, recommendations = run(user_id=23333)
    print("Recommendations generated in %s seconds" % (time.time() - start_time))
    print("Similar users:", similar_users)
    print("Recommended recipes:", recommendations)


if __name__ == "__main__":
    test_recommender()
