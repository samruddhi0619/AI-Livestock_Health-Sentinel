from datetime import datetime, timedelta, timezone
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
import bcrypt

from config import settings
from database import db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against its bcrypt hashed counterpart.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """
    Hashes a password using bcrypt.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a signed JWT access token.
    """
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now_utc})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Validates the bearer token and retrieves the authenticated user document.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials. Token may be invalid or expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db["users"].find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user

class RoleChecker:
    """
    Role-Based Access Control (RBAC) Dependency.
    Permits access only if the user's role is in the allowed roles list.
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = [r.upper() for r in allowed_roles]
        
    def __call__(self, current_user: dict = Depends(get_current_user)) -> dict:
        user_role = str(current_user.get("role", "")).upper()
        # ADMIN always has full supervisory privileges
        if user_role == "ADMIN":
            return current_user
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Role '{user_role}' lacks permission for this endpoint. Required: {self.allowed_roles}"
            )
        return current_user

# Pre-configured RBAC dependencies
require_farmer = RoleChecker(["FARMER"])
require_veterinarian = RoleChecker(["VETERINARIAN"])
require_admin = RoleChecker(["ADMIN"])
require_clinician = RoleChecker(["VETERINARIAN", "ADMIN"])
require_authenticated = get_current_user
