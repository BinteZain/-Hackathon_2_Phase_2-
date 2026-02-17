"""
Security Tests for Chat API Endpoints.

These tests verify that the chat endpoints properly enforce JWT authentication
and user isolation as per the security requirements:

1. Require JWT on all chat requests
2. Verify JWT using BETTER_AUTH_SECRET from environment
3. Extract user_id from token
4. Ensure URL user_id matches token user_id
5. Pass only authenticated user_id to MCP tools
6. Enforce user isolation in all DB queries
7. Return 401 if no token
8. Return 403 if mismatch

Run with:
    pytest tests/test_chat_security.py -v
"""

import pytest
import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.main import app
from src.database.config import settings
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message
from src.utils.jwt import create_access_token, verify_token, settings as jwt_settings


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture(name="session")
def session_fixture():
    """Create a new database session for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with database override."""
    def get_session_override():
        return session

    app.dependency_overrides[Session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a test user."""
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        username="testuser"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_user_2")
def test_user_2_fixture(session: Session):
    """Create a second test user."""
    user = User(
        id=str(uuid.uuid4()),
        email="test2@example.com",
        username="testuser2"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="auth_token")
def auth_token_fixture(test_user: User):
    """Create a valid JWT token for test user."""
    return create_access_token({"user_id": test_user.id})


@pytest.fixture(name="token_user_2")
def token_user_2_fixture(test_user_2: User):
    """Create a valid JWT token for second test user."""
    return create_access_token({"user_id": test_user_2.id})


# ============================================================================
# Test: JWT Token Verification
# ============================================================================

class TestJWTTokenVerification:
    """Test JWT token creation and verification."""

    def test_create_access_token(self, test_user: User):
        """Test that access tokens can be created."""
        token = create_access_token({"user_id": test_user.id})
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_valid_token(self, test_user: User, auth_token: str):
        """Test that valid tokens can be verified."""
        token_data = verify_token(auth_token)
        assert token_data.user_id == test_user.id

    def test_verify_token_extracts_user_id(self, test_user: User, auth_token: str):
        """Test that user_id is correctly extracted from token sub claim."""
        token_data = verify_token(auth_token)
        assert token_data.user_id is not None
        assert token_data.user_id == test_user.id

    def test_verify_invalid_token(self):
        """Test that invalid tokens raise 401."""
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token("invalid_token")
        
        assert exc_info.value.status_code == 401

    def test_verify_expired_token(self, test_user: User):
        """Test that expired tokens raise 401."""
        from fastapi import HTTPException
        from jose import jwt
        from datetime import datetime, timedelta
        
        # Create expired token
        expire = datetime.utcnow() - timedelta(hours=1)
        to_encode = {
            "exp": expire,
            "sub": test_user.id,
            "user_id": test_user.id
        }
        expired_token = jwt.encode(
            to_encode,
            jwt_settings.BETTER_AUTH_SECRET,
            algorithm="HS256"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(expired_token)
        
        assert exc_info.value.status_code == 401

    def test_verify_token_without_user_id(self):
        """Test that tokens without user_id raise 401."""
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
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == 401


# ============================================================================
# Test: Authentication Requirements (401)
# ============================================================================

class TestAuthenticationRequired:
    """Test that all chat endpoints require authentication."""

    def test_chat_endpoint_requires_token(self, client: TestClient):
        """Test that chat endpoint returns 401 without token."""
        response = client.post(
            "/api/test-user-id/chat",
            json={"message": "Hello"}
        )
        assert response.status_code == 401
        assert "Authorization" in response.json()["detail"] or "auth" in response.json()["detail"].lower()

    def test_conversations_list_requires_token(self, client: TestClient, test_user: User):
        """Test that conversations list endpoint returns 401 without token."""
        response = client.get(f"/api/{test_user.id}/conversations")
        assert response.status_code == 401

    def test_conversation_detail_requires_token(self, client: TestClient, test_user: User):
        """Test that conversation detail endpoint returns 401 without token."""
        response = client.get(f"/api/{test_user.id}/conversations/1")
        assert response.status_code == 401

    def test_conversation_delete_requires_token(self, client: TestClient, test_user: User):
        """Test that conversation delete endpoint returns 401 without token."""
        response = client.delete(f"/api/{test_user.id}/conversations/1")
        assert response.status_code == 401


# ============================================================================
# Test: User ID Matching (403)
# ============================================================================

class TestUserIDMatching:
    """Test that URL user_id must match token user_id."""

    def test_chat_user_id_mismatch_returns_403(
        self, client: TestClient, test_user: User, test_user_2: User, token_user_2: str
    ):
        """Test that chat endpoint returns 403 when URL user_id doesn't match token."""
        response = client.post(
            f"/api/{test_user.id}/chat",  # URL has user_1's ID
            json={"message": "Hello"},
            headers={"Authorization": f"Bearer {token_user_2}"}  # Token has user_2's ID
        )
        assert response.status_code == 403
        assert "mismatch" in response.json()["detail"].lower() or "does not match" in response.json()["detail"].lower()

    def test_conversations_list_user_id_mismatch_returns_403(
        self, client: TestClient, test_user: User, test_user_2: User, token_user_2: str
    ):
        """Test that conversations list returns 403 when user_id doesn't match."""
        response = client.get(
            f"/api/{test_user.id}/conversations",  # URL has user_1's ID
            headers={"Authorization": f"Bearer {token_user_2}"}  # Token has user_2's ID
        )
        assert response.status_code == 403

    def test_conversation_detail_user_id_mismatch_returns_403(
        self, client: TestClient, test_user: User, test_user_2: User, token_user_2: str
    ):
        """Test that conversation detail returns 403 when user_id doesn't match."""
        response = client.get(
            f"/api/{test_user.id}/conversations/1",  # URL has user_1's ID
            headers={"Authorization": f"Bearer {token_user_2}"}  # Token has user_2's ID
        )
        assert response.status_code == 403

    def test_conversation_delete_user_id_mismatch_returns_403(
        self, client: TestClient, test_user: User, test_user_2: User, token_user_2: str
    ):
        """Test that conversation delete returns 403 when user_id doesn't match."""
        response = client.delete(
            f"/api/{test_user.id}/conversations/1",  # URL has user_1's ID
            headers={"Authorization": f"Bearer {token_user_2}"}  # Token has user_2's ID
        )
        assert response.status_code == 403

    def test_chat_user_id_match_succeeds(
        self, client: TestClient, test_user: User, auth_token: str
    ):
        """Test that chat endpoint succeeds when user_id matches token."""
        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"message": "Hello"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Should not be 401 or 403 (may be other errors like 404 for user not found in test DB)
        assert response.status_code not in [401, 403]


# ============================================================================
# Test: User Isolation in Database Queries
# ============================================================================

class TestUserIsolation:
    """Test that database queries enforce user isolation."""

    def test_user_can_only_access_own_conversations(
        self, client: TestClient, session: Session,
        test_user: User, test_user_2: User, auth_token: str
    ):
        """Test that users can only access their own conversations."""
        # Create conversation for user_2
        conversation = Conversation(
            user_id=test_user_2.id,
            title="User 2's Conversation"
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        # Try to access user_2's conversation as user_1
        response = client.get(
            f"/api/{test_user.id}/conversations/{conversation.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Should return 403 (forbidden) or 404 (not found)
        assert response.status_code in [403, 404]

    def test_user_cannot_access_another_users_messages(
        self, client: TestClient, session: Session,
        test_user: User, test_user_2: User, auth_token: str
    ):
        """Test that users cannot access another user's messages."""
        # Create conversation and message for user_2
        conversation = Conversation(
            user_id=test_user_2.id,
            title="User 2's Conversation"
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        message = Message(
            user_id=test_user_2.id,
            conversation_id=conversation.id,
            role="user",
            content="Private message"
        )
        session.add(message)
        session.commit()

        # Try to list conversations - should only see own conversations
        response = client.get(
            f"/api/{test_user.id}/conversations",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Should not see user_2's conversations
        for conv in data["conversations"]:
            assert conv["user_id"] == test_user.id

    def test_conversation_ownership_verified(
        self, client: TestClient, session: Session,
        test_user: User, test_user_2: User, auth_token: str
    ):
        """Test that conversation ownership is verified before access."""
        # Create conversation for user_1
        conversation = Conversation(
            user_id=test_user.id,
            title="User 1's Conversation"
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        # User 1 should be able to access their own conversation
        response = client.get(
            f"/api/{test_user.id}/conversations/{conversation.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Should succeed (200) or fail due to test DB setup (not auth)
        assert response.status_code not in [401, 403]


# ============================================================================
# Test: Environment Variable Configuration
# ============================================================================

class TestEnvironmentConfiguration:
    """Test that secrets are loaded from environment."""

    def test_better_auth_secret_loaded_from_env(self):
        """Test that BETTER_AUTH_SECRET is loaded from environment."""
        assert jwt_settings.BETTER_AUTH_SECRET is not None
        assert jwt_settings.BETTER_AUTH_SECRET != ""
        assert jwt_settings.BETTER_AUTH_SECRET != "your-secret-key-here"

    def test_better_auth_secret_not_hardcoded(self):
        """Test that secret is not a common hardcoded value."""
        common_secrets = [
            "secret",
            "password",
            "123456",
            "admin",
            "test",
            "your-secret-key-here",
            "change-me",
        ]
        assert jwt_settings.BETTER_AUTH_SECRET.lower() not in common_secrets

    def test_token_verification_uses_env_secret(self, test_user: User):
        """Test that token verification uses the environment secret."""
        # Create token with current secret
        token = create_access_token({"user_id": test_user.id})
        
        # Should verify successfully
        token_data = verify_token(token)
        assert token_data.user_id == test_user.id


# ============================================================================
# Test: MCP Tool User Isolation
# ============================================================================

class TestMCPToolUserIsolation:
    """Test that MCP tools enforce user isolation."""

    def test_mcp_tools_receive_authenticated_user_id(
        self, client: TestClient, session: Session,
        test_user: User, auth_token: str
    ):
        """Test that only authenticated user_id is passed to MCP tools."""
        # This test verifies the chat endpoint properly passes user_id
        # The actual MCP tool isolation is tested in test_mcp_tools.py
        
        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"message": "List my tasks"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Should not return 401 or 403
        # (May return 500 if MCP server not available in test env)
        assert response.status_code not in [401, 403]

    def test_user_cannot_impersonate_another_user(
        self, client: TestClient, session: Session,
        test_user: User, test_user_2: User, auth_token: str
    ):
        """Test that users cannot impersonate others via MCP tools."""
        # Try to make a request with user_1's token but user_2's ID in path
        response = client.post(
            f"/api/{test_user_2.id}/chat",
            json={"message": "List my tasks"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Should return 403 Forbidden
        assert response.status_code == 403


# ============================================================================
# Test: Authorization Header Format
# ============================================================================

class TestAuthorizationHeaderFormat:
    """Test that Authorization header format is properly validated."""

    def test_missing_authorization_header(self, client: TestClient, test_user: User):
        """Test that missing Authorization header returns 401."""
        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"message": "Hello"}
        )
        assert response.status_code == 401

    def test_invalid_authorization_header_format(self, client: TestClient, test_user: User):
        """Test that invalid Authorization header format returns 401."""
        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"message": "Hello"},
            headers={"Authorization": "InvalidFormat token123"}
        )
        assert response.status_code == 401

    def test_bearer_prefix_required(self, client: TestClient, test_user: User, auth_token: str):
        """Test that Bearer prefix is required."""
        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"message": "Hello"},
            headers={"Authorization": auth_token}  # Missing "Bearer " prefix
        )
        assert response.status_code == 401

    def test_valid_bearer_token_succeeds(self, client: TestClient, test_user: User, auth_token: str):
        """Test that valid Bearer token is accepted."""
        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"message": "Hello"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Should pass authentication (may fail for other reasons in test env)
        assert response.status_code not in [401, 403]


# ============================================================================
# Integration Tests
# ============================================================================

class TestSecurityIntegration:
    """Integration tests for complete security flow."""

    def test_complete_auth_flow(self, client: TestClient, session: Session, test_user: User):
        """Test complete authentication flow from token to database query."""
        # 1. Create token
        token = create_access_token({"user_id": test_user.id})
        
        # 2. Make authenticated request
        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"message": "Hello"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 3. Verify authentication passed (not 401/403)
        assert response.status_code not in [401, 403]

    def test_token_expiration_enforced(self, client: TestClient, test_user: User):
        """Test that expired tokens are rejected."""
        from jose import jwt
        from datetime import datetime, timedelta
        
        # Create expired token
        expire = datetime.utcnow() - timedelta(hours=1)
        to_encode = {
            "exp": expire,
            "sub": test_user.id,
            "user_id": test_user.id
        }
        expired_token = jwt.encode(
            to_encode,
            jwt_settings.BETTER_AUTH_SECRET,
            algorithm="HS256"
        )
        
        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"message": "Hello"},
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401

    def test_tampered_token_rejected(self, client: TestClient, test_user: User, auth_token: str):
        """Test that tampered tokens are rejected."""
        # Tamper with the token
        tampered_token = auth_token[:-5] + "XXXXX"
        
        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"message": "Hello"},
            headers={"Authorization": f"Bearer {tampered_token}"}
        )
        
        assert response.status_code == 401
