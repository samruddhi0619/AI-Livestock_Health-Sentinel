import os
import sys
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "backend"))

from database import db, is_mock_db

print(f"is_mock_db: {is_mock_db}")
if is_mock_db:
    print(f"db_path: {db.db_path}")
    print(f"db_path exists: {os.path.exists(db.db_path)}")
    
    with open(db.db_path, "r") as f:
        content = json.load(f)
    print(f"Raw file keys: {list(content.keys())}")
    if "users" in content:
        print(f"Raw file users count: {len(content['users'])}")
        print(f"Raw file user names: {[u['username'] for u in content['users']]}")
    else:
        print("Raw file does not contain 'users' key!")

users_in_db = db["users"].find()
print(f"db['users'].find() count: {len(users_in_db)}")
print(f"db['users'].find() names: {[u['username'] for u in users_in_db]}")
