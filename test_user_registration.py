import requests
import json

# Define the API base URL
BASE_URL = "http://localhost:4000/api/v1"

# Test user data
test_user = {
    "email": "test@example.com",
    "password": "password123",
    "username": "testuser"
}

print("Registering test user...")
response = requests.post(f"{BASE_URL}/auth/register", json=test_user)

if response.status_code == 200:
    data = response.json()
    print(f"Registration successful: {data['message']}")
    print(f"Token: {data['token'][:20]}...")  # Print first 20 chars of token
    
    # Now try to login with the same credentials
    print("\nTrying to login with the registered user...")
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if login_response.status_code == 200:
        login_data = login_response.json()
        print(f"Login successful: {login_data['message']}")
        print(f"User ID: {login_data['user']['id']}")
        print("Authentication is working correctly!")
    else:
        print(f"Login failed: {login_response.json()}")
else:
    print(f"Registration failed: {response.json()}")