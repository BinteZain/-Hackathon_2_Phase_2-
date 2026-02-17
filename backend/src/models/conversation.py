from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List
import uuid


# Handle circular import
if TYPE_CHECKING:
    from .user import User
    from .message import Message


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: int = Field(primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: Optional[List["Message"]] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class ConversationRead(SQLModel):
    id: int
    user_id: uuid.UUID
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ConversationCreate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=255)


class ConversationUpdate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=255)
