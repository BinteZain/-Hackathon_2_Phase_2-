#!/usr/bin/env python
"""
A minimal FastAPI application to test the backend server.
"""

import os
import sys
from contextlib import suppress

# Add the backend/src directory to the Python path
backend_src = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_src)

# Set environment variables
os.environ.setdefault('DATABASE_URL', 'sqlite:///./todoapp.db')
os.environ.setdefault('BETTER_AUTH_SECRET', 'your-super-secret-better-auth-key-here-make-it-long-and-random')

# Temporarily disable the problematic model initialization
# by monkey-patching SQLModel.metadata.create_all
original_create_all = None

try:
    from sqlmodel import SQLModel
    
    # Store the original method
    original_create_all = SQLModel.metadata.create_all
    
    # Replace with a no-op function
    def noop_create_all(*args, **kwargs):
        print("SQLModel.metadata.create_all called but skipped for testing purposes")
    
    SQLModel.metadata.create_all = noop_create_all
    
    # Now import the main app
    from main import app
    
    # Restore the original method
    if original_create_all:
        SQLModel.metadata.create_all = original_create_all

    import uvicorn

    if __name__ == "__main__":
        print("Starting backend server on http://localhost:4000...")
        print("Database URL:", os.environ.get('DATABASE_URL'))
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=4000,
            reload=False,  # Disable reload to avoid import issues
            app_dir="./backend/src"
        )
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying to run a minimal server instead...")
    
    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI(title="Minimal Test Server")
    
    @app.get("/")
    def read_root():
        return {"message": "Server started but with limited functionality due to import issues"}
    
    if __name__ == "__main__":
        print("Starting minimal server on http://localhost:4000...")
        uvicorn.run(app, host="0.0.0.0", port=4000)