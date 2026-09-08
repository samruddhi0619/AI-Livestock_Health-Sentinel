import os
import sys

# Ensure backend directory is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT_DIR, "backend"))

from generate_demo_data import seed_data

if __name__ == "__main__":
    print("==================================================")
    print("Seeding AI-Livestock Health Sentinel Demo Database")
    print("==================================================")
    seed_data()
    print("Database seeding completed successfully.")
