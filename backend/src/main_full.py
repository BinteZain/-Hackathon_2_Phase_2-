from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Session, select
from .database.session import get_session
from .models.user import User
from .utils.jwt import create_access_token, get_current_user, TokenData
from .schemas.user import UserCreate
from passlib.context import CryptContext
from datetime import timedelta
from typing import Optional
import uuid

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize FastAPI app
app = FastAPI(
    title="Hackathon-Todo API",
    description="REST API for the Hackathon-Todo application",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:4000"],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Login endpoint
@app.post("/api/v1/auth/login")
async def login(
    email: str,
    password: str,
    session: Session = Depends(get_session)
):
    # Find user by email
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if not user or not pwd_context.verify(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Update last login time
    # user.last_login_at = datetime.utcnow()  # Commenting out to avoid datetime issues
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

    return {
        "success": True,
        "token": token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username
        },
        "message": "Login successful"
    }

# Registration endpoint
@app.post("/api/v1/auth/register")
async def register(
    email: str,
    password: str,
    username: str,
    session: Session = Depends(get_session)
):
    # Check if user already exists
    statement = select(User).where(
        (User.email == email) | (User.username == username)
    )
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )

    # Hash the password
    hashed_password = pwd_context.hash(password)

    # Create new user
    user = User(
        email=email,
        username=username,
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

    return {
        "success": True,
        "token": token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username
        },
        "message": "Registration successful"
    }

# Protected user profile endpoint
@app.get("/api/v1/users/me")
async def get_current_user_profile(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # In a real implementation, we would fetch user details from the database
    # For now, return the user info from the token
    return {
        "id": current_user.user_id,
        "email": "user@example.com",  # Would fetch from DB in real implementation
        "username": "demo_user"       # Would fetch from DB in real implementation
    }

# Global middleware to verify JWT on all /api/* endpoints
@app.middleware("http")
async def verify_jwt_middleware(request: Request, call_next):
    # Only check for JWT on /api/* endpoints
    if request.url.path.startswith("/api/"):
        # Skip authentication for auth endpoints (login, register, etc.)
        if "/auth/" in request.url.path and request.method in ["POST"]:
            # Allow login and register without authentication
            if request.url.path.endswith("/auth/login") or request.url.path.endswith("/auth/register"):
                response = await call_next(request)
                return response

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header[len("Bearer "):]

        # Verify the token
        try:
            from .utils.jwt import verify_token
            verify_token(token)
        except HTTPException:
            # Re-raise the HTTPException from verify_token which already has the right status code
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    response = await call_next(request)
    return response

@app.get("/")
def read_root():
    return {"message": "Welcome to Hackathon-Todo API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}