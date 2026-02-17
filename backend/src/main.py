from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .database.session import engine
from .models.task import Task  # Import models to register them with SQLModel
from .models.user import User  # Import User model to register it with SQLModel
from sqlmodel import SQLModel
from .routes import tasks
from .routes.auth import router as auth_router
from .routes.users import router as users_router
from .routes.chat import router as chat_router
from .utils.jwt import verify_token, TokenData

# Create tables
SQLModel.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Hackathon-Todo API",
    description="REST API for the Hackathon-Todo application",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:4000",
        "http://127.0.0.1:4000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Include routes
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(users_router, prefix="/api/v1", tags=["users"])
app.include_router(chat_router, tags=["chat"])

# Global middleware to verify JWT on all /api/* endpoints
@app.middleware("http")
async def verify_jwt_middleware(request: Request, call_next):
    # Skip JWT verification for OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        response = await call_next(request)
        return response
    
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
            token_data = verify_token(token)
            # Store token data in request state for later use
            request.state.token_data = token_data
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