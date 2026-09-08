import os

class Settings:
    PROJECT_NAME: str = "AI-Livestock Health Sentinel"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "metaminds_sih2026_sentinel_secret_key_secure")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # MongoDB Config
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    DATABASE_NAME: str = "livestock_sentinel"
    
    # Storage
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    DATA_DIR: str = os.path.join(os.path.dirname(__file__), "data")
    
    # Server configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.DATA_DIR, exist_ok=True)
