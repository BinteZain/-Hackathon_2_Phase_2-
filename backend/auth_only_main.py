import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from routes.auth import router as auth_router
from utils.jwt import verify_token

# Initialize FastAPI app
app = FastAPI(
    title="Hackathon-Todo API - Auth Only",
    description="Authentication endpoints for the Hackathon-Todo API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only auth routes
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])

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
    return {"message": "Auth-only API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "sqlite (dev)"}