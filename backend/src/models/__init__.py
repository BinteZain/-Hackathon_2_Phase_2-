"""SQLModel database models for the application."""

from .user import User, UserRead, UserCreate, UserUpdate
from .task import Task, TaskRead, TaskCreate, TaskUpdate
from .conversation import (
    Conversation,
    ConversationRead,
    ConversationCreate,
    ConversationUpdate,
)
from .message import (
    Message,
    MessageRead,
    MessageCreate,
    MessageUpdate,
)
from .mcp_tool_execution import (
    MCPToolExecution,
    MCPToolExecutionRead,
    MCPToolExecutionCreate,
)

__all__ = [
    # User
    "User",
    "UserRead",
    "UserCreate",
    "UserUpdate",
    # Task
    "Task",
    "TaskRead",
    "TaskCreate",
    "TaskUpdate",
    # Conversation
    "Conversation",
    "ConversationRead",
    "ConversationCreate",
    "ConversationUpdate",
    # Message
    "Message",
    "MessageRead",
    "MessageCreate",
    "MessageUpdate",
    # MCP Tool Execution
    "MCPToolExecution",
    "MCPToolExecutionRead",
    "MCPToolExecutionCreate",
]
