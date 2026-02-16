from fastapi import FastAPI, Request, HTTPException, status, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import Optional
import uuid
import sqlite3
import hashlib
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize FastAPI app
app = FastAPI(
    title="Hackathon-Todo API - Auth Enabled",
    description="Development version of the Hackathon-Todo API with authentication",
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

# Helper function to get database connection
def get_db_connection():
    conn = sqlite3.connect('todoapp.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

# JWT utility functions (simplified for this implementation)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    import time
    import jwt
    from .database.config import settings
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire.timestamp(), "sub": data.get("user_id")})
    encoded_jwt = jwt.encode(to_encode, settings.BETTER_AUTH_SECRET, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str):
    import jwt
    from .database.config import settings
    
    try:
        payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"user_id": user_id}
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Login endpoint
@app.post("/api/v1/auth/login")
async def login(
    email: str = Form(...),
    password: str = Form(...)
):
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Find user by email
        cursor.execute("SELECT * FROM user WHERE email = ?", (email,))
        user_row = cursor.fetchone()
        
        if not user_row or not pwd_context.verify(password, user_row['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Update last login time
        cursor.execute(
            "UPDATE user SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?",
            (user_row['id'],)
        )
        conn.commit()
        
        # Create JWT token with user id as "sub"
        token_data = {
            "user_id": user_row['id'],
            "email": user_row['email'],
            "username": user_row['username']
        }
        token = create_access_token(
            data=token_data,
            expires_delta=timedelta(days=7)  # Token expires in 7 days
        )
        
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user_row['id'],
                "email": user_row['email'],
                "username": user_row['username']
            },
            "message": "Login successful"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}"
        )
    finally:
        conn.close()

# Registration endpoint
@app.post("/api/v1/auth/register")
async def register(
    email: str = Form(...),
    password: str = Form(...),
    username: str = Form(...)
):
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user already exists
        cursor.execute("SELECT * FROM user WHERE email = ? OR username = ?", (email, username))
        existing_user = cursor.fetchone()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered"
            )
        
        # Hash the password
        hashed_password = pwd_context.hash(password)
        
        # Create new user
        user_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO user (id, email, username, password_hash) 
            VALUES (?, ?, ?, ?)
        ''', (user_id, email, username, hashed_password))
        
        conn.commit()
        
        # Create JWT token with user id as "sub"
        token_data = {
            "user_id": user_id,
            "email": email,
            "username": username
        }
        token = create_access_token(
            data=token_data,
            expires_delta=timedelta(days=7)  # Token expires in 7 days
        )
        
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user_id,
                "email": email,
                "username": username
            },
            "message": "Registration successful"
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {str(e)}"
        )
    finally:
        conn.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Hackathon-Todo API - Authentication Enabled"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}