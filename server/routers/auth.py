# Authentication routes for the AI Agent System
# This file handles user authentication using only a username

# Routes:
# - POST /api/v1/auth/signup: Create a new user account
# - POST /api/v1/auth/login: Authenticate user and return JWT token
# - POST /api/v1/auth/refresh: Refresh an expired JWT token
# - GET /api/v1/auth/me: Get current user information
# - POST /api/v1/auth/change-password: Change user password

# Functions:
# - create_access_token(): Generate JWT tokens for authenticated users
# - get_password_hash(): Hash user passwords for secure storage
# - verify_password(): Validate password against stored hash
# - get_current_user(): Dependency to extract and validate user from token 

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from models.db import get_db
from models.user import User, create_user_with_username, get_user_by_username

# Load environment variables
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Pydantic models for request/response
class UserLogin(BaseModel):
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    username: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class TokenData(BaseModel):
    email: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Generate JWT token with expiration time"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Dependency to extract and validate current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    user = get_user_by_username(username, db)
    
    if user is None:
        raise credentials_exception
        
    return user

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account"""
    # Check if user already exists
    db_user = get_user_by_username(user_data.username, db)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    new_user = create_user_with_username(user_data.username, db)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user with username only and return JWT token"""
    # Get user or create if not exists
    user = get_user_by_username(user_login.username, db)
    
    if not user:
        # Create user if they don't exist
        user = create_user_with_username(user_login.username, db)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {"username": current_user.username}

@router.post("/change-password", response_model=UserResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    if not current_user.verify_password(password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password"
        )
    
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    return current_user 