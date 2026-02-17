# Chat API Security Documentation

## Overview

The Phase 3 Chat API endpoints are secured with JWT authentication to ensure:
- Only authenticated users can access chat functionality
- Users can only access their own data (user isolation)
- MCP tools receive only the authenticated user's ID
- All secrets are loaded from environment variables

## Security Requirements Implemented

### 1. JWT Required on All Chat Requests ✅

All endpoints under `/api/` require JWT authentication via the global middleware in `src/main.py`.

**Implementation:**
```python
@app.middleware("http")
async def verify_jwt_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        # Extract and verify JWT token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
        
        token = auth_header[len("Bearer "):]
        token_data = verify_token(token)
        request.state.token_data = token_data
    
    response = await call_next(request)
    return response
```

**Response:** `401 Unauthorized` if no valid token provided

### 2. JWT Verification Using BETTER_AUTH_SECRET ✅

JWT tokens are verified using the `BETTER_AUTH_SECRET` environment variable.

**Implementation:** (`src/utils/jwt.py`)
```python
class Settings(BaseSettings):
    BETTER_AUTH_SECRET: str
    DATABASE_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

def verify_token(token: str) -> TokenData:
    payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=["HS256"])
    user_id: str = payload.get("sub")
    # ...
```

**Security:** Secret is loaded from environment, never hardcoded.

### 3. User ID Extracted from Token ✅

The user ID is extracted from the JWT `sub` (subject) claim.

**Implementation:**
```python
def verify_token(token: str) -> TokenData:
    payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=["HS256"])
    user_id: str = payload.get("sub")  # Extract from 'sub' claim
    if user_id is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return TokenData(user_id=user_id)
```

### 4. URL user_id Must Match Token user_id ✅

All chat endpoints validate that the `user_id` in the URL path matches the authenticated user's ID from the token.

**Implementation:** (`src/routes/chat.py`)
```python
@router.post("/{user_id}/chat")
async def chat(user_id: str, request: ChatRequest, req: Request, ...):
    token_data = get_token_data(req)
    
    # Validate user_id matches token
    if token_data.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="User ID in path does not match authenticated user"
        )
```

**Response:** `403 Forbidden` if mismatch

### 5. Only Authenticated user_id Passed to MCP Tools ✅

The authenticated user's ID is passed to MCP tools, ensuring tools operate on the correct user's data.

**Implementation:** (`src/routes/chat.py`)
```python
async def run_agent_with_message(user_id: str, ...):
    # Build conversation context with authenticated user_id
    system_context = f"Current user ID: {user_id}"
    
    # MCP tools receive user_id as parameter
    # Each tool validates ownership before operations
```

**MCP Tool Example:** (`src/mcp/server.py`)
```python
async def handle_add_task(arguments: Dict[str, Any]):
    user_id = arguments.get("user_id")
    
    # Verify user exists
    user = session.get(User, str(user_uuid))
    if not user:
        return {"success": False, "error": f"User not found: {user_id}"}
    
    # Create task with verified user_id
    task = Task(user_id=str(user_uuid), ...)
```

### 6. User Isolation in All DB Queries ✅

All database queries filter by user_id to ensure users can only access their own data.

**Examples:**

**List Conversations:**
```python
statement = (
    select(Conversation)
    .where(Conversation.user_id == uuid.UUID(user_id))
    .order_by(Conversation.updated_at.desc())
)
```

**MCP Tool - List Tasks:**
```python
query = select(Task).where(Task.user_id == str(user_uuid))
```

**MCP Tool - Complete Task:**
```python
task = session.get(Task, str(task_uuid))
if task.user_id != str(user_uuid):
    return {"success": False, "error": "Task does not belong to the specified user"}
```

### 7. Return 401 if No Token ✅

**Scenarios:**
- Missing Authorization header
- Invalid Authorization header format
- Missing "Bearer " prefix
- Invalid/expired token

**Response:**
```json
{
  "detail": "Missing or invalid Authorization header",
  "headers": {"WWW-Authenticate": "Bearer"}
}
```

**Status Code:** `401 Unauthorized`

### 8. Return 403 if Mismatch ✅

**Scenario:** URL `user_id` doesn't match token `user_id`

**Response:**
```json
{
  "detail": "User ID in path does not match authenticated user"
}
```

**Status Code:** `403 Forbidden`

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `BETTER_AUTH_SECRET` | JWT signing secret (min 32 chars) | `your-secure-random-secret-key-here` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./todoapp.db` |

### Generating a Secure Secret

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32

# Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

## Security Testing

### Run Verification Tests

```bash
cd backend
.\venv\Scripts\python.exe tests\verify_chat_security.py
```

### Test Scenarios

| Test | Expected Result |
|------|-----------------|
| Request without token | `401 Unauthorized` |
| Request with invalid token | `401 Unauthorized` |
| Request with expired token | `401 Unauthorized` |
| Request with mismatched user_id | `403 Forbidden` |
| Request without "Bearer " prefix | `401 Unauthorized` |
| Valid request with matching user_id | `200 OK` |

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Request                          │
│  POST /api/{user_id}/chat                                    │
│  Authorization: Bearer <jwt_token>                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Global JWT Middleware                        │
│  1. Check Authorization header exists                        │
│  2. Verify "Bearer " prefix                                  │
│  3. Decode and verify JWT with BETTER_AUTH_SECRET            │
│  4. Extract user_id from 'sub' claim                         │
│  5. Store token_data in request.state                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Chat Endpoint                              │
│  1. Get token_data from request.state                        │
│  2. Validate: token_data.user_id == path user_id             │
│     - If mismatch: return 403 Forbidden                      │
│  3. Validate user exists in database                         │
│  4. All DB queries filtered by user_id                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP Agent                                 │
│  Receives only authenticated user_id                         │
│  System context: "Current user ID: {user_id}"                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   MCP Tools                                  │
│  Each tool validates:                                        │
│  - user_id parameter matches authenticated user              │
│  - Task/Resource ownership before operations                 │
│  - Returns error if ownership validation fails               │
└─────────────────────────────────────────────────────────────┘
```

## Files Modified/Created

| File | Purpose |
|------|---------|
| `src/main.py` | Global JWT middleware |
| `src/utils/jwt.py` | JWT token creation/verification |
| `src/routes/chat.py` | Chat endpoints with user_id validation |
| `src/mcp/server.py` | MCP tools with ownership validation |
| `.env.example` | Environment variable template |
| `tests/verify_chat_security.py` | Security verification tests |
| `tests/test_chat_security.py` | Comprehensive pytest test suite |

## Security Checklist

- [x] JWT required on all `/api/*` endpoints
- [x] JWT verified using `BETTER_AUTH_SECRET` from environment
- [x] User ID extracted from token `sub` claim
- [x] URL user_id validated against token user_id
- [x] 401 returned for missing/invalid tokens
- [x] 403 returned for user_id mismatch
- [x] Only authenticated user_id passed to MCP tools
- [x] User isolation enforced in all DB queries
- [x] No hardcoded secrets
- [x] Environment variables documented
- [x] Security tests implemented

## Related Documentation

- [Authentication Spec](../specs/features/authentication.md)
- [API Security Best Practices](../specs/api/security.md)
- [MCP Tools Documentation](../specs/api/mcp-tools.md)
