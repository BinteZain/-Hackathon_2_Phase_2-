import sqlite3
import hashlib
import uuid
from datetime import datetime

# Connect to the SQLite database
conn = sqlite3.connect('todoapp.db')
cursor = conn.cursor()

# Create the users table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email_verified BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    first_name TEXT,
    last_name TEXT
)
''')

# Hash a password (using a simple hash for demo purposes)
# In a real app, you'd use bcrypt as implemented in the backend
def simple_hash_password(password):
    # This is just for demonstration - in real app use bcrypt
    return hashlib.sha256(password.encode()).hexdigest()

# Create a test user
test_user_id = str(uuid.uuid4())
test_email = "test@example.com"
test_username = "testuser"
test_password = "password123"
hashed_password = simple_hash_password(test_password)

try:
    cursor.execute('''
    INSERT INTO user (id, email, username, password_hash) 
    VALUES (?, ?, ?, ?)
    ''', (test_user_id, test_email, test_username, hashed_password))
    
    conn.commit()
    print("Test user created successfully!")
    print(f"Email: {test_email}")
    print(f"Password: {test_password}")
    print(f"User ID: {test_user_id}")
except sqlite3.IntegrityError:
    print("Test user already exists")

conn.close()