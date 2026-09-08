from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from database import db
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from schemas import UserRegister, UserLogin, TokenResponse, UserOut, UserRole

router = APIRouter(prefix="/api/auth", tags=["Authentication & User Management"])

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Registers a new user with a specific role (FARMER, VETERINARIAN, or ADMIN)."
)
def register(user_data: UserRegister):
    # 1. Validate username uniqueness
    existing_user = db["users"].find_one({"username": user_data.username.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user_data.username}' is already registered."
        )
        
    # 2. Hash password securely
    hashed_password = get_password_hash(user_data.password)
    
    # 3. Create user document
    now_str = datetime.now(timezone.utc).isoformat()
    user_doc = {
        "username": user_data.username.lower(),
        "password": hashed_password,
        "fullname": user_data.fullname,
        "role": user_data.role.value,
        "phone": user_data.phone or "",
        "village": user_data.village or "",
        "taluka": user_data.taluka or "",
        "district": user_data.district or "",
        "license_number": user_data.license_number or "",
        "is_active": True,
        "created_at": now_str,
        "updated_at": now_str
    }
    
    res = db["users"].insert_one(user_doc)
    
    return {
        "success": True,
        "message": f"User '{user_data.username}' registered successfully as {user_data.role.value}.",
        "user_id": res.inserted_id,
        "role": user_data.role.value
    }

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate User",
    description="Authenticates credentials and issues a signed JWT access token."
)
def login(credentials: UserLogin):
    user = db["users"].find_one({"username": credentials.username.lower()})
    if not user or not verify_password(credentials.password, user.get("password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been deactivated. Please contact an administrator."
        )
        
    # Generate JWT token with sub and role claims
    role = str(user.get("role", "FARMER")).upper()
    access_token = create_access_token(
        data={"sub": user["username"], "role": role, "user_id": str(user.get("_id", user.get("id", "")))}
    )
    
    user_out = {
        "id": str(user.get("_id", user.get("id", ""))),
        "username": user["username"],
        "fullname": user.get("fullname", ""),
        "role": role,
        "phone": user.get("phone", ""),
        "district": user.get("district", ""),
        "taluka": user.get("taluka", ""),
        "village": user.get("village", ""),
        "license_number": user.get("license_number", ""),
        "is_active": user.get("is_active", True)
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_out
    }

@router.get(
    "/me",
    response_model=UserOut,
    summary="Current User Profile",
    description="Returns the profile information of the currently authenticated user."
)
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user.get("_id", current_user.get("id", ""))),
        "username": current_user["username"],
        "fullname": current_user.get("fullname", ""),
        "role": current_user.get("role", "FARMER"),
        "phone": current_user.get("phone", ""),
        "district": current_user.get("district", ""),
        "taluka": current_user.get("taluka", ""),
        "village": current_user.get("village", ""),
        "license_number": current_user.get("license_number", ""),
        "is_active": current_user.get("is_active", True)
    }
