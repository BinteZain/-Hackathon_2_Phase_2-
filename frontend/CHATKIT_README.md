# ChatKit UI Integration

This directory contains the ChatKit UI integration for the Todo Assistant application.

## Overview

The ChatKit integration provides an AI-powered chat interface for interacting with the Todo Assistant. It uses the `@openai/chatkit` library for the UI component and integrates with the custom backend REST API.

## Features

- **Hosted ChatKit UI**: Uses the official `@openai/chatkit` library for a polished, production-ready chat interface
- **JWT Authentication**: Sends JWT token in the `Authorization: Bearer <token>` header with every request
- **Custom Backend Integration**: Calls `POST /api/{user_id}/chat` endpoint
- **Conversation Management**: Maintains `conversation_id` in component state for persistent conversations
- **Assistant Responses**: Displays AI assistant responses with support for tool call visualization

## Files

- `src/pages/chatkit-hosted.tsx` - Main ChatKit page component
- `src/lib/chatApi.ts` - API client for chat operations (used by other pages)

## Setup

### 1. Environment Variables

Configure the following environment variables in `frontend/.env`:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:4000

# ChatKit Configuration
# Get your domain key from: https://platform.openai.com/settings/organization/security/domain-allowlist
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your-domain-key
```

### 2. Install Dependencies

```bash
cd hackathon-todo
npm install
```

The `@openai/chatkit` package is already included in the root `package.json`.

### 3. Run the Application

```bash
# Start the frontend
cd frontend
npm run dev

# Start the backend (in another terminal)
cd backend
python -m uvicorn src.main:app --reload --port 4000
```

Navigate to `http://localhost:3000/chatkit-hosted` to access the ChatKit UI.

## Usage

### Authentication

The ChatKit page requires authentication. Users must be logged in to access the chat interface. The JWT token is automatically retrieved from `localStorage` and included in API requests.

### Conversation Flow

1. **New Conversation**: When a user sends their first message, a new conversation is created automatically
2. **Conversation ID**: The `conversation_id` is stored in component state and included in subsequent messages
3. **Message History**: ChatKit automatically manages and displays conversation history
4. **Tool Calls**: When the assistant uses tools (create task, list tasks, etc.), they are displayed inline

### State Management

The `conversation_id` is maintained in React state:

```typescript
const [conversationId, setConversationId] = useState<number | null>(null);
```

This ensures:
- Continuity within a session
- Proper context for the backend
- Ability to switch between conversations

## API Integration

### Request Format

The ChatKit component sends requests to:

```
POST /api/{user_id}/chat
Headers:
  Authorization: Bearer <jwt_token>
  Content-Type: application/json
Body:
  {
    "message": "User's message content",
    "conversation_id": 123  // optional, null for new conversation
  }
```

### Response Format

Expected response from the backend:

```json
{
  "success": true,
  "conversation_id": 123,
  "response": "Assistant's response text",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "arguments": { "title": "Buy groceries" },
      "result": { "success": true, "id": 456 }
    }
  ],
  "message_id": 789,
  "created_at": "2025-02-17T10:30:00Z"
}
```

## Customization

### UI Theme

Modify the `theme` option in `chatkit-hosted.tsx`:

```typescript
theme: {
  colorScheme: 'light',  // or 'dark'
  radius: 'pill',        // 'pill' | 'round' | 'soft' | 'sharp'
  density: 'normal',     // 'compact' | 'normal' | 'spacious'
}
```

### Starter Prompts

Customize the prompts shown on the start screen:

```typescript
startScreen: {
  greeting: 'Hello! I\'m your Todo Assistant...',
  prompts: [
    {
      label: 'Add a task',
      prompt: 'Add a task to buy groceries',
      icon: 'plus',
    },
    // Add more prompts...
  ],
}
```

## Troubleshooting

### "User ID not found in authentication token"

- Ensure you're logged in
- Check that the JWT token is stored in `localStorage`
- Verify the token contains a valid `sub` claim

### "Failed to initialize ChatKit"

- Check that `@openai/chatkit` is installed
- Verify the CSS import: `import '@openai/chatkit/dist/index.css'`
- Check browser console for detailed error messages

### Backend Connection Errors

- Ensure the backend is running on the configured `NEXT_PUBLIC_API_URL`
- Verify CORS settings allow requests from the frontend origin
- Check that the JWT token is valid and not expired

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  ChatKit UI     │────▶│  Custom Fetch    │────▶│  Backend API    │
│  (@openai/      │     │  (JWT + Transform)│     │  POST /api/     │
│   chatkit)      │◀────│                  │◀────│  {user_id}/chat │
└─────────────────┘     └──────────────────┘     └─────────────────┘
       │                                              │
       │                                              ▼
       │                                     ┌─────────────────┐
       │                                     │  AI Agent       │
       │                                     │  (MCP Tools)    │
       │                                     └─────────────────┘
       ▼
┌─────────────────┐
│ conversation_id │
│ State Management│
└─────────────────┘
```

## Related Documentation

- [ChatKit JS Documentation](https://openai.github.io/chatkit-js/)
- [ChatKit Python SDK](https://openai.github.io/chatkit-python/)
- [Backend Chat API](../backend/src/routes/chat.py)
