import os
import json
import uuid
from datetime import datetime
from config import settings

class MockCollection:
    def __init__(self, db_path, collection_name):
        self.db_path = db_path
        self.name = collection_name
        
    def _load_data(self):
        if not os.path.exists(self.db_path):
            # Create empty structure
            with open(self.db_path, "w") as f:
                json.dump({}, f)
            return {}
        try:
            with open(self.db_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}
            
    def _save_data(self, data):
        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
            
    def _match(self, doc, query):
        if not query:
            return True
        for k, v in query.items():
            if k == "_id" and isinstance(v, dict) and "$in" in v:
                if doc.get("_id") not in v["$in"]:
                    return False
                continue
            if k == "animal_id" and isinstance(v, dict) and "$in" in v:
                if doc.get("animal_id") not in v["$in"]:
                    return False
                continue
            if doc.get(k) != v:
                return False
        return True

    def insert_one(self, doc):
        data = self._load_data()
        if self.name not in data:
            data[self.name] = []
            
        doc = doc.copy()
        if "_id" not in doc:
            doc["_id"] = str(uuid.uuid4())
            
        # Serialize datetime fields
        for k, v in doc.items():
            if isinstance(v, datetime):
                doc[k] = v.isoformat()
                
        data[self.name].append(doc)
        self._save_data(data)
        
        class InsertOneResult:
            inserted_id = doc["_id"]
        return InsertOneResult()

    def find(self, query=None):
        data = self._load_data()
        docs = data.get(self.name, [])
        matched = [d for d in docs if self._match(d, query)]
        
        # Cursor wrapper to support sort and limit chaining
        class MockCursor(list):
            def sort(self, key_or_list, direction=None):
                field = key_or_list
                reverse = (direction == -1)
                if isinstance(key_or_list, list):
                    field = key_or_list[0][0]
                    reverse = (key_or_list[0][1] == -1)
                # Sort elements based on field
                def sort_key(x):
                    val = x.get(field, "")
                    return val if val is not None else ""
                self.sort(key=sort_key, reverse=reverse)
                return self
                
            def limit(self, count):
                return MockCursor(self[:count])
                
        return MockCursor(matched)

    def find_one(self, query=None):
        res = self.find(query)
        return res[0] if res else None

    def update_one(self, query, update):
        data = self._load_data()
        docs = data.get(self.name, [])
        updated = 0
        for doc in docs:
            if self._match(doc, query):
                if "$set" in update:
                    for k, v in update["$set"].items():
                        if isinstance(v, datetime):
                            v = v.isoformat()
                        doc[k] = v
                if "$push" in update:
                    for k, v in update["$push"].items():
                        if isinstance(v, datetime):
                            v = v.isoformat()
                        if k not in doc:
                            doc[k] = []
                        doc[k].append(v)
                updated += 1
                break # only update first matching item
        if updated > 0:
            self._save_data(data)
            
        class UpdateResult:
            modified_count = updated
        return UpdateResult()

    def delete_one(self, query):
        data = self._load_data()
        docs = data.get(self.name, [])
        deleted = 0
        for i, doc in enumerate(docs):
            if self._match(doc, query):
                docs.pop(i)
                deleted += 1
                break
        if deleted > 0:
            self._save_data(data)
            
        class DeleteResult:
            deleted_count = deleted
        return DeleteResult()

    def count_documents(self, query=None):
        return len(self.find(query))

class MockDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        
    def __getitem__(self, collection_name):
        return MockCollection(self.db_path, collection_name)

# Database Connection Initialization
db = None
is_mock_db = False

# Try to connect to real MongoDB if URI is supplied
if settings.MONGODB_URI:
    try:
        from pymongo import MongoClient
        print(f"Connecting to MongoDB Atlas/Service at: {settings.MONGODB_URI}...")
        client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=2000)
        # Force a connection check
        client.server_info()
        db = client[settings.DATABASE_NAME]
        print("Connected to MongoDB successfully!")
    except Exception as e:
        print(f"MongoDB connection failed: {e}. Falling back to file-based JSON DB.")
        db = None

if db is None:
    db_json_path = os.path.join(settings.DATA_DIR, "db.json")
    db = MockDatabase(db_json_path)
    is_mock_db = True
    print(f"Database running in JSON-file Local Sandbox Mode. Storage: {db_json_path}")
