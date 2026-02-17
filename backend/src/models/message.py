from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List, Dict, Any
import uuid

from sqlalchemy import CheckConstraint, JSON, Column

# Handle circular import
if TYPE_CHECKING:
    from .user import User
    from .conversation import Conversation
    from .mcp_tool_execution import MCPToolExecution


class Message(SQLModel, table=True):
    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant', 'system')",
            name="check_role_valid"
        ),
    )

    id: int = Field(primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field()
    content: str = Field()
    message_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column("message_metadata", JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="messages")
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
    tool_executions: Optional[List["MCPToolExecution"]] = Relationship(
        back_populates="message",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class MessageRead(SQLModel):
    id: int
    user_id: uuid.UUID
    conversation_id: int
    role: str
    content: str
    message_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime


class MessageCreate(SQLModel):
    role: str = Field()
    content: str = Field()
    message_metadata: Optional[Dict[str, Any]] = Field(default=None)


class MessageUpdate(SQLModel):
    content: Optional[str] = Field(default=None)
    message_metadata: Optional[Dict[str, Any]] = Field(default=None)
