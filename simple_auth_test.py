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

print("Attempting to register a test user...")
try:
    response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
    print(f"Registration response status: {response.status_code}")
    print(f"Registration response: {response.text}")
    
    if response.status_code == 200:
        print("Registration successful!")
        data = response.json()
        token = data.get('token')
        print(f"Received token: {token[:20] if token else 'None'}...")
    else:
        print("Registration failed.")
        
    # Now try to login with the same credentials
    print("\nTrying to login with the registered user...")
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login response status: {login_response.status_code}")
    print(f"Login response: {login_response.text}")
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        print(f"Login successful: {login_data.get('message', 'Success')}")
        print(f"User ID: {login_data['user'].get('id', 'N/A')}")
        print("Authentication is working correctly!")
    else:
        print("Login failed.")
        
except requests.exceptions.ConnectionError:
    print("Could not connect to the backend. Please make sure the backend server is running on http://localhost:4000")
except Exception as e:
    print(f"An error occurred: {e}")