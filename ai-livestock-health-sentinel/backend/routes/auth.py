from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from database import db
from auth import get_password_hash, verify_password, create_access_token
from models import UserRegister, UserLogin
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register")
def register(user: UserRegister):
    # Check if user already exists
    existing_user = db["users"].find_one({"username": user.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
        
    hashed_password = get_password_hash(user.password)
    user_doc = {
        "username": user.username,
        "password": hashed_password,
        "fullname": user.fullname,
        "role": user.role.upper(),
        "phone": user.phone,
        "village": user.village,
        "taluka": user.taluka,
        "district": user.district,
        "created_at": datetime.utcnow().isoformat()
    }
    
    db["users"].insert_one(user_doc)
    return {"message": "User registered successfully"}

@router.post("/login")
def login(credentials: UserLogin):
    user = db["users"].find_one({"username": credentials.username})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "fullname": user["fullname"]
    }
