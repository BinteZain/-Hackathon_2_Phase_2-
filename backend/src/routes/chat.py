"""
Chat API endpoints for AI-powered conversations.

This module provides endpoints for users to interact with an AI assistant
that can manage tasks through natural language conversations.
"""

import asyncio
import uuid
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from pydantic import BaseModel, Field

from ..database.session import get_session
from ..models.user import User
from ..models.conversation import Conversation, ConversationCreate, ConversationRead
from ..models.message import Message, MessageCreate, MessageRead
from ..utils.jwt import verify_token, TokenData


router = APIRouter(prefix="/api", tags=["chat"])

security = HTTPBearer()


# ============================================================================
# Request/Response Models
# ============================================================================

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=4000, description="User's message")
    conversation_id: Optional[int] = Field(default=None, description="Existing conversation ID (creates new if not provided)")


class ToolCall(BaseModel):
    """Represents a tool call made by the agent."""
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    success: bool
    conversation_id: int
    response: str
    tool_calls: List[ToolCall] = []
    message_id: int
    created_at: datetime


class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history."""
    success: bool
    conversation: ConversationRead
    messages: List[MessageRead]


class ConversationListResponse(BaseModel):
    """Response model for listing conversations."""
    success: bool
    conversations: List[ConversationRead]
    total: int


# ============================================================================
# Helper Functions
# ============================================================================

def get_token_data(request: Request) -> TokenData:
    """Get token data from request state (set by middleware)."""
    token_data = getattr(request.state, 'token_data', None)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data


async def run_agent_with_message(
    user_id: str,
    message: str,
    conversation_history: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Run the AI agent with the user's message and conversation history.
    
    Returns:
        Dict with 'response' (text) and 'tool_calls' (list of tool call details)
    """
    # Import here to avoid circular imports
    from agents import Agent, Runner, set_tracing_disabled
    from agents.mcp import MCPServerStdio
    
    # Disable tracing
    set_tracing_disabled(True)
    
    # Create MCP server connection
    mcp_server = MCPServerStdio(
        name="todo-app",
        command="python",
        args=["-m", "src.mcp.run"],
    )
    
    try:
        # Connect to MCP server
        await mcp_server.connect()
        
        # Get tools from MCP server
        mcp_tools = await mcp_server.list_tools()
        
        # Create agent with MCP tools
        agent = Agent(
            name="Todo Assistant",
            instructions="""You are a friendly Todo Assistant. Help users manage tasks through conversation.
            
When the user asks you to do something with tasks (create, list, complete, update, delete),
use the available tools to help them. Always be friendly and confirm destructive actions.

For task operations, you need the user's ID which will be provided in the context.""",
            tools=mcp_tools,
            model="gpt-4o-mini",
        )
        
        # Build conversation context with user_id
        system_context = f"Current user ID: {user_id}"
        
        # Build messages for the conversation
        messages = [{"role": "system", "content": system_context}]
        messages.extend(conversation_history[-20:])  # Last 20 messages for context
        messages.append({"role": "user", "content": message})
        
        # Run the agent
        result = await Runner.run(agent, messages)
        
        # Extract tool calls from the result if available
        tool_calls = []
        if hasattr(result, 'tool_calls') and result.tool_calls:
            for tc in result.tool_calls:
                tool_calls.append({
                    "tool_name": tc.name if hasattr(tc, 'name') else str(tc),
                    "arguments": tc.arguments if hasattr(tc, 'arguments') else {},
                    "result": tc.result if hasattr(tc, 'result') else None
                })
        
        return {
            "response": result.final_output if hasattr(result, 'final_output') else str(result),
            "tool_calls": tool_calls
        }
        
    finally:
        # Disconnect from MCP server
        await mcp_server.disconnect()


# ============================================================================
# Chat Endpoints
# ============================================================================

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    req: Request,
    session: Session = Depends(get_session)
):
    """
    Send a message to the AI assistant and get a response.
    
    Flow:
    1. Verify JWT token (done by middleware)
    2. Validate user_id matches token
    3. Fetch or create conversation
    4. Store user message
    5. Run agent with conversation history
    6. Store assistant response
    7. Return response with tool calls
    """
    # Step 1 & 2: Get token data and validate user_id matches token
    token_data = get_token_data(req)
    if token_data.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID in path does not match authenticated user"
        )
    
    # Validate user exists
    user = session.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Step 3: Fetch or create conversation
    conversation = None
    if request.conversation_id:
        conversation = session.get(Conversation, request.conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {request.conversation_id} not found"
            )
        # Verify ownership
        if str(conversation.user_id) != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Conversation does not belong to user"
            )
    else:
        # Create new conversation
        conversation = Conversation(user_id=uuid.UUID(user_id), title="New Conversation")
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
    
    # Step 4: Store user message
    user_message = Message(
        user_id=uuid.UUID(user_id),
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    session.add(user_message)
    session.commit()
    session.refresh(user_message)
    
    # Fetch conversation history for context
    messages_statement = (
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
    )
    messages = session.exec(messages_statement).all()
    
    # Convert to format for agent
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]
    
    # Step 5: Run agent
    try:
        agent_result = await run_agent_with_message(
            user_id=user_id,
            message=request.message,
            conversation_history=conversation_history
        )
    except Exception as e:
        # Rollback user message on agent failure
        session.delete(user_message)
        session.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )
    
    # Step 6: Store assistant response
    assistant_message = Message(
        user_id=uuid.UUID(user_id),
        conversation_id=conversation.id,
        role="assistant",
        content=agent_result["response"],
        metadata={"tool_calls": agent_result["tool_calls"]} if agent_result["tool_calls"] else None
    )
    session.add(assistant_message)
    
    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    
    # Auto-generate title from first message if default
    if conversation.title == "New Conversation" and len(request.message) > 0:
        # Use first 50 chars of first message as title
        conversation.title = request.message[:50] + ("..." if len(request.message) > 50 else "")
    
    session.add(conversation)
    session.commit()
    session.refresh(assistant_message)
    
    # Step 7: Return response
    tool_calls = [
        ToolCall(
            tool_name=tc.get("tool_name", "unknown"),
            arguments=tc.get("arguments", {}),
            result=tc.get("result")
        )
        for tc in agent_result["tool_calls"]
    ]
    
    return ChatResponse(
        success=True,
        conversation_id=conversation.id,
        response=agent_result["response"],
        tool_calls=tool_calls,
        message_id=assistant_message.id,
        created_at=assistant_message.created_at
    )


@router.get("/{user_id}/conversations", response_model=ConversationListResponse)
async def list_conversations(
    user_id: str,
    req: Request,
    session: Session = Depends(get_session),
    limit: int = 50,
    offset: int = 0
):
    """List all conversations for the authenticated user."""
    # Validate user_id matches token
    token_data = get_token_data(req)
    if token_data.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID in path does not match authenticated user"
        )
    
    # Validate user exists
    user = session.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Fetch conversations
    statement = (
        select(Conversation)
        .where(Conversation.user_id == uuid.UUID(user_id))
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    conversations = session.exec(statement).all()
    
    # Get total count
    count_statement = select(Conversation).where(Conversation.user_id == uuid.UUID(user_id))
    total = len(session.exec(count_statement).all())
    
    return ConversationListResponse(
        success=True,
        conversations=[
            ConversationRead(
                id=c.id,
                user_id=c.user_id,
                title=c.title,
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            for c in conversations
        ],
        total=total
    )


@router.get("/{user_id}/conversations/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation(
    user_id: str,
    conversation_id: int,
    req: Request,
    session: Session = Depends(get_session)
):
    """Get a specific conversation with its message history."""
    # Validate user_id matches token
    token_data = get_token_data(req)
    if token_data.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID in path does not match authenticated user"
        )
    
    # Fetch conversation
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Verify ownership
    if str(conversation.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conversation does not belong to user"
        )
    
    # Fetch messages
    messages_statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = session.exec(messages_statement).all()
    
    return ConversationHistoryResponse(
        success=True,
        conversation=ConversationRead(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        ),
        messages=[
            MessageRead(
                id=m.id,
                user_id=m.user_id,
                conversation_id=m.conversation_id,
                role=m.role,
                content=m.content,
                metadata=m.metadata,
                created_at=m.created_at
            )
            for m in messages
        ]
    )


@router.delete("/{user_id}/conversations/{conversation_id}")
async def delete_conversation(
    user_id: str,
    conversation_id: int,
    req: Request,
    session: Session = Depends(get_session)
):
    """Delete a conversation and all its messages."""
    # Validate user_id matches token
    token_data = get_token_data(req)
    if token_data.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID in path does not match authenticated user"
        )
    
    # Fetch conversation
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Verify ownership
    if str(conversation.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conversation does not belong to user"
        )
    
    # Delete conversation (messages cascade delete)
    session.delete(conversation)
    session.commit()
    
    return {"success": True, "message": "Conversation deleted"}
