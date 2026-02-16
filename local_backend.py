import os
import sys
from pathlib import Path

# Add the backend/src directory to the Python path
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

# Set environment variables to use SQLite
os.environ.setdefault('DATABASE_URL', 'sqlite:///./todoapp.db')
os.environ.setdefault('BETTER_AUTH_SECRET', 'your-super-secret-better-auth-key-here-make-it-long-and-random')

def create_minimal_app():
    """Create a minimal FastAPI app that avoids problematic imports."""
    from fastapi import FastAPI
    
    app = FastAPI(
        title="Hackathon-Todo API - Local Dev",
        description="Development version of the Hackathon-Todo API",
        version="1.0.0"
    )
    
    @app.get("/")
    def read_root():
        return {"message": "Hackathon-Todo API is running locally!"}
    
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "database": "sqlite (dev)"}
    
    return app

if __name__ == "__main__":
    print("Starting local development server...")
    print("Using SQLite database for development")
    
    app = create_minimal_app()
    
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=4000,
        reload=False,
        log_level="info"
    )