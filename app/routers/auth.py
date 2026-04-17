from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta
from uuid import UUID
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, Token, UserResponse
from app.auth import verify_password, get_password_hash, create_access_token
from app.utils import generate_verification_token, send_verification_email
from app.config import settings
from app.dependencies import get_current_user
import re

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Check if email exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate username from email (before @ symbol)
    username_base = user_data.email.split('@')[0]
    # Remove any special characters for username
    username_base = re.sub(r'[^a-zA-Z0-9_]', '', username_base)
    
    # Make username unique by adding random suffix if needed
    username = username_base
    counter = 1
    while True:
        existing_username = db.query(User).filter(User.username == username).first()
        if not existing_username:
            break
        username = f"{username_base}{counter}"
        counter += 1
    
    # Create verification token
    verification_token = generate_verification_token()
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=username,
        email=user_data.email,
        hashed_password=hashed_password,
        email_verification_token=verification_token,
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Send verification email in background
    background_tasks.add_task(
        send_verification_email,
        new_user.email,
        new_user.username,
        verification_token
    )
    
    return new_user

@router.post("/login", response_model=Token)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    # Find user by email only (matching your frontend)
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated. Please verify your email."
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    token_data = {"sub": str(user.id), "email": user.email, "username": user.username, "role": user.role}
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Ensure we return a string, not a tuple
    if isinstance(access_token, tuple):
        access_token = access_token[0]
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.options("/login")
def options_login():
    return {"message": "OK"}

@router.options("/register")
def options_register():
    return {"message": "OK"}

@router.options("/me")
def options_me():
    return {"message": "OK"}