import requests
import os
import sys
from pathlib import Path

# Add the backend/src directory to the Python path
backend_src = Path(__file__).parent / 'backend' / 'src'
sys.path.insert(0, str(backend_src))

# Set environment variables
os.environ.setdefault('database_url', 'sqlite:///./todoapp.db')

# Import the app and database modules directly
from sqlmodel import SQLModel, Session
from backend.src.database.session import engine
from backend.src.models.user import User
from passlib.context import CryptContext

# Create tables
SQLModel.metadata.create_all(bind=engine)

# Create a test user
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

with Session(engine) as session:
    # Check if user already exists
    existing_user = session.query(User).filter(User.email == "test@example.com").first()
    
    if not existing_user:
        # Create a new test user
        hashed_password = pwd_context.hash("password123")
        test_user = User(
            email="test@example.com",
            username="testuser",
            password_hash=hashed_password
        )
        session.add(test_user)
        session.commit()
        print("Test user created successfully")
    else:
        print("Test user already exists")

# Now test the API endpoints
BASE_URL = "http://localhost:4000/api/v1"

print("\nTesting registration...")
register_data = {
    "email": "newuser@example.com",
    "password": "password123",
    "username": "newuser"
}

response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print(f"Registration response: {response.status_code}, {response.text}")

print("\nTesting login with test user...")
login_data = {
    "email": "test@example.com",
    "password": "password123"
}

response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
print(f"Login response: {response.status_code}, {response.text}")

if response.status_code == 200:
    token = response.json().get('token')
    print(f"\nLogin successful! Token: {token[:20]}..." if token else "No token returned")
    
    # Test accessing a protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    profile_response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
    print(f"Profile response: {profile_response.status_code}, {profile_response.text}")
else:
    print("\nLogin failed. The backend might not be running or there might be an issue with the auth routes.")