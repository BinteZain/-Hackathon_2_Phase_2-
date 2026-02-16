from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import timedelta, datetime
from ..database.session import get_session
from ..models.user import User
from ..utils.jwt import create_access_token
from pydantic import BaseModel
from typing import Optional
import uuid
from passlib.context import CryptContext

router = APIRouter(prefix="/auth", tags=["auth"])

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str

class LoginResponse(BaseModel):
    success: bool
    token: str
    user: dict
    message: str

@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, session: Session = Depends(get_session)):
    """
    Authenticate user and return JWT token
    """
    # Find user by email
    statement = select(User).where(User.email == login_data.email)
    user = session.exec(statement).first()

    if not user or not pwd_context.verify(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Update last login time
    user.last_login_at = datetime.utcnow()
    session.add(user)
    session.commit()

    # Create JWT token with user id as "sub"
    token_data = {
        "user_id": str(user.id),  # Include user id
        "email": user.email,
        "username": user.username
    }
    token = create_access_token(
        data=token_data,
        expires_delta=timedelta(days=7)  # Token expires in 7 days
    )

    return LoginResponse(
        success=True,
        token=token,
        user={
            "id": str(user.id),
            "email": user.email,
            "username": user.username
        },
        message="Login successful"
    )

@router.post("/register", response_model=LoginResponse)
def register(register_data: RegisterRequest, session: Session = Depends(get_session)):
    """
    Register a new user and return JWT token
    """
    # Check if user already exists
    statement = select(User).where(
        (User.email == register_data.email) | (User.username == register_data.username)
    )
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )

    # Hash the password
    hashed_password = pwd_context.hash(register_data.password)

    # Create new user
    user = User(
        email=register_data.email,
        username=register_data.username,
        password_hash=hashed_password
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Create JWT token with user id as "sub"
    token_data = {
        "user_id": str(user.id),  # Include user id
        "email": user.email,
        "username": user.username
    }
    token = create_access_token(
        data=token_data,
        expires_delta=timedelta(days=7)  # Token expires in 7 days
    )

    return LoginResponse(
        success=True,
        token=token,
        user={
            "id": str(user.id),
            "email": user.email,
            "username": user.username
        },
        message="Registration successful"
    )

@router.post("/logout")
def logout():
    """
    Logout user (client-side token removal is sufficient)
    """
    return {"success": True, "message": "Logout successful"}

@router.get("/profile")
def get_profile():
    """
    Get profile of authenticated user
    """
    # This would normally use the JWT token to identify the user
    # Since this is just a placeholder, we'll return a mock response
    # The actual implementation would extract user info from the token
    return {"message": "Profile endpoint - requires authentication"}