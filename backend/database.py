import os
import time
import json
import uuid
from datetime import datetime, timezone
from typing import Generator, Dict, Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError

from config import settings

# ---------------------------------------------------------------------------
# 1. PostgreSQL SQLAlchemy 2.0 Connection
# ---------------------------------------------------------------------------
postgres_available = False
engine = None
SessionLocal = None

try:
    # Attempt to initialize PostgreSQL engine
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_pre_ping=True
    )
    # Test ping with short timeout
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    postgres_available = True
    print(f"[DATABASE] Connected successfully to PostgreSQL at {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
except Exception as e:
    # Graceful fallback: SQLite / Sandbox engine for offline development and testing
    fallback_db_path = os.path.join(settings.DATA_DIR, "sandbox.db")
    engine = create_engine(f"sqlite:///{fallback_db_path}", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    postgres_available = False
    print(f"[DATABASE] PostgreSQL offline or unreachable. Initialized local SQLite fallback at {fallback_db_path}")

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding an active SQLAlchemy database session.
    """
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

def check_database_health() -> Dict[str, Any]:
    """
    Executes a heartbeat query against the database and measures response latency.
    """
    t0 = time.perf_counter()
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "status": "UP",
            "database_connected": postgres_available,
            "database_mode": "PostgreSQL 16 (Production)" if postgres_available else "Local Sandbox Engine",
            "engine_dialect": str(engine.dialect.name),
            "latency_ms": latency_ms,
            "message": "Database operational and accepting queries."
        }
    except Exception as exc:
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "status": "DEGRADED",
            "database_connected": False,
            "database_mode": "Local Sandbox Engine",
            "engine_dialect": str(engine.dialect.name) if engine else "unknown",
            "latency_ms": latency_ms,
            "message": f"Connection check failed: {str(exc)}"
        }

# ---------------------------------------------------------------------------
# 2. Backward-Compatible Collection Adapter (for existing endpoints)
# ---------------------------------------------------------------------------
class MockCollection:
    def __init__(self, db_path: str, collection_name: str):
        self.db_path = db_path
        self.name = collection_name
        
    def _load_data(self):
        if not os.path.exists(self.db_path):
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
        if "$or" in query and isinstance(query["$or"], list):
            return any(self._match(doc, subq) for subq in query["$or"])
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
        for k, v in doc.items():
            if isinstance(v, datetime):
                doc[k] = v.isoformat()
        data[self.name].append(doc)
        self._save_data(data)
        
        class InsertResult:
            inserted_id = doc["_id"]
        return InsertResult()

    def find(self, query=None, limit=0, sort=None):
        data = self._load_data().get(self.name, [])
        matched = [d for d in data if self._match(d, query)]
        if sort:
            key, direction = sort[0]
            matched.sort(key=lambda x: x.get(key, ""), reverse=(direction == -1))
        if limit > 0:
            matched = matched[:limit]
        return matched

    def find_one(self, query=None):
        res = self.find(query, limit=1)
        return res[0] if res else None

    def update_one(self, query, update):
        data = self._load_data()
        items = data.get(self.name, [])
        for doc in items:
            if self._match(doc, query):
                if "$set" in update:
                    for k, v in update["$set"].items():
                        doc[k] = v.isoformat() if isinstance(v, datetime) else v
                self._save_data(data)
                return True
        return False

    def count_documents(self, query=None):
        return len(self.find(query))

    def delete_one(self, query):
        data = self._load_data()
        items = data.get(self.name, [])
        for i, doc in enumerate(items):
            if self._match(doc, query):
                items.pop(i)
                self._save_data(data)
                return True
        return False

class MockDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def __getitem__(self, name: str):
        return MockCollection(self.db_path, name)

# Local storage path for backward compatible file DB
JSON_DB_PATH = os.path.join(settings.DATA_DIR, "db.json")
db = MockDatabase(JSON_DB_PATH)
is_mock_db = not postgres_available
