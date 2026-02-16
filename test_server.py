import os
import sys
from pathlib import Path

# Add the backend/src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "backend/src"))

# Set the environment variable for the database
os.environ.setdefault("DATABASE_URL", "sqlite:///./todoapp.db")

# Import and run the application
from fastapi import FastAPI
import uvicorn

# Create a minimal app for testing
app = FastAPI(title="Test Server")

@app.get("/")
def read_root():
    return {"message": "Server is running"}

if __name__ == "__main__":
    print("Starting server on http://localhost:4000")
    uvicorn.run(app, host="0.0.0.0", port=4000)