#!/usr/bin/env python3
"""
Security Verification Script for Chat API.

This script verifies that the chat endpoints properly enforce JWT authentication
and user isolation without requiring pytest.

Run with:
    python tests/verify_chat_security.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.jwt import create_access_token, verify_token, settings as jwt_settings
from datetime import datetime, timedelta
import uuid


def test_jwt_token_creation():
    """Test JWT token creation."""
    print("\n[PASS] Test: JWT Token Creation")
    
    user_id = str(uuid.uuid4())
    token = create_access_token({"user_id": user_id})
    
    assert token is not None, "Token should not be None"
    assert isinstance(token, str), "Token should be a string"
    assert len(token) > 0, "Token should not be empty"
    assert len(token.split('.')) == 3, "Token should have 3 parts (header.payload.signature)"
    
    print(f"  - Created token: {token[:50]}...")
    print("  PASSED\n")
    return True


def test_jwt_token_verification():
    """Test JWT token verification."""
    print("\n[PASS] Test: JWT Token Verification")
    
    user_id = str(uuid.uuid4())
    token = create_access_token({"user_id": user_id})
    
    token_data = verify_token(token)
    
    assert token_data.user_id == user_id, f"Expected user_id {user_id}, got {token_data.user_id}"
    
    print(f"  - Extracted user_id: {token_data.user_id}")
    print("  PASSED\n")
    return True


def test_jwt_extracts_user_id_from_sub():
    """Test that user_id is extracted from token 'sub' claim."""
    print("\n[PASS] Test: User ID Extraction from 'sub' Claim")
    
    user_id = str(uuid.uuid4())
    token = create_access_token({"user_id": user_id})
    
    token_data = verify_token(token)
    
    assert token_data.user_id is not None, "user_id should not be None"
    assert token_data.user_id == user_id, f"Expected {user_id}, got {token_data.user_id}"
    
    print(f"  - 'sub' claim correctly mapped to user_id: {token_data.user_id}")
    print("  PASSED\n")
    return True


def test_better_auth_secret_from_env():
    """Test that BETTER_AUTH_SECRET is loaded from environment."""
    print("\n[PASS] Test: BETTER_AUTH_SECRET from Environment")
    
    secret = jwt_settings.BETTER_AUTH_SECRET
    
    assert secret is not None, "BETTER_AUTH_SECRET should not be None"
    assert secret != "", "BETTER_AUTH_SECRET should not be empty"
    assert secret != "your-secret-key-here", "BETTER_AUTH_SECRET should not be default value"
    assert len(secret) >= 32, f"BETTER_AUTH_SECRET should be at least 32 chars, got {len(secret)}"
    
    print(f"  - BETTER_AUTH_SECRET length: {len(secret)} chars")
    print("  PASSED\n")
    return True


def test_invalid_token_rejected():
    """Test that invalid tokens are rejected."""
    print("\n[PASS] Test: Invalid Token Rejection")
    
    from fastapi import HTTPException
    
    try:
        verify_token("invalid_token_xyz")
        print("  FAILED - Should have raised HTTPException\n")
        return False
    except HTTPException as e:
        assert e.status_code == 401, f"Expected 401, got {e.status_code}"
        print(f"  - Invalid token correctly rejected with status {e.status_code}")
        print("  PASSED\n")
        return True


def test_expired_token_rejected():
    """Test that expired tokens are rejected."""
    print("\n[PASS] Test: Expired Token Rejection")
    
    from fastapi import HTTPException
    from jose import jwt
    
    user_id = str(uuid.uuid4())
    
    # Create expired token
    expire = datetime.utcnow() - timedelta(hours=1)
    to_encode = {
        "exp": expire,
        "sub": user_id,
        "user_id": user_id
    }
    expired_token = jwt.encode(
        to_encode,
        jwt_settings.BETTER_AUTH_SECRET,
        algorithm="HS256"
    )
    
    try:
        verify_token(expired_token)
        print("  FAILED - Should have raised HTTPException\n")
        return False
    except HTTPException as e:
        assert e.status_code == 401, f"Expected 401, got {e.status_code}"
        print(f"  - Expired token correctly rejected with status {e.status_code}")
        print("  PASSED\n")
        return True


def test_token_without_user_id_rejected():
    """Test that tokens without user_id are rejected."""
    print("\n[PASS] Test: Token Without User ID Rejection")
    
    from fastapi import HTTPException
    from jose import jwt
    
    # Create token without sub/user_id
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode = {
        "exp": expire,
        "some_other_claim": "value"
    }
    token = jwt.encode(
        to_encode,
        jwt_settings.BETTER_AUTH_SECRET,
        algorithm="HS256"
    )
    
    try:
        verify_token(token)
        print("  FAILED - Should have raised HTTPException\n")
        return False
    except HTTPException as e:
        assert e.status_code == 401, f"Expected 401, got {e.status_code}"
        print(f"  - Token without user_id correctly rejected with status {e.status_code}")
        print("  PASSED\n")
        return True


def test_middleware_protects_api_endpoints():
    """Test that middleware protects API endpoints."""
    print("\n[PASS] Test: Middleware Protection for API Endpoints")
    
    from src.main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # Test without token
    response = client.post("/api/some-user/chat", json={"message": "test"})
    
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    print(f"  - Unauthenticated request correctly rejected with status {response.status_code}")
    print("  PASSED\n")
    return True


def test_user_id_mismatch_returns_403():
    """Test that user_id mismatch returns 403."""
    print("\n[PASS] Test: User ID Mismatch Returns 403")
    
    from src.main import app
    from fastapi.testclient import TestClient
    from sqlmodel import Session, SQLModel, create_engine
    from sqlmodel.pool import StaticPool
    
    # Create test database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    def get_session_override():
        with Session(engine) as session:
            yield session
    
    app.dependency_overrides[Session] = get_session_override
    
    try:
        client = TestClient(app)
        
        # Create two users
        user_1_id = str(uuid.uuid4())
        user_2_id = str(uuid.uuid4())
        
        # Create token for user_2
        token = create_access_token({"user_id": user_2_id})
        
        # Try to access user_1's endpoint with user_2's token
        response = client.post(
            f"/api/{user_1_id}/chat",
            json={"message": "test"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print(f"  - User ID mismatch correctly rejected with status {response.status_code}")
        print("  PASSED\n")
        return True
    finally:
        app.dependency_overrides.clear()


def test_authorization_header_format():
    """Test that Authorization header format is validated."""
    print("\n[PASS] Test: Authorization Header Format Validation")
    
    from src.main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    user_id = str(uuid.uuid4())
    
    # Test without "Bearer " prefix
    response = client.post(
        f"/api/{user_id}/chat",
        json={"message": "test"},
        headers={"Authorization": "some-token"}
    )
    
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    print(f"  - Invalid header format correctly rejected with status {response.status_code}")
    print("  PASSED\n")
    return True


def main():
    """Run all security verification tests."""
    print("\n" + "="*70)
    print("  Chat API Security Verification")
    print("="*70)
    
    tests = [
        ("JWT Token Creation", test_jwt_token_creation),
        ("JWT Token Verification", test_jwt_token_verification),
        ("User ID Extraction from 'sub'", test_jwt_extracts_user_id_from_sub),
        ("BETTER_AUTH_SECRET from Environment", test_better_auth_secret_from_env),
        ("Invalid Token Rejection", test_invalid_token_rejected),
        ("Expired Token Rejection", test_expired_token_rejected),
        ("Token Without User ID Rejection", test_token_without_user_id_rejected),
        ("Middleware Protection", test_middleware_protects_api_endpoints),
        ("User ID Mismatch Returns 403", test_user_id_mismatch_returns_403),
        ("Authorization Header Format", test_authorization_header_format),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  FAILED - {name}: {str(e)}\n")
            failed += 1
    
    print("\n" + "="*70)
    print(f"  Results: {passed} passed, {failed} failed")
    print("="*70)
    
    if failed > 0:
        print("\nWARNING: Some tests failed. Review the output above.")
        sys.exit(1)
    else:
        print("\nSUCCESS: All security tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
