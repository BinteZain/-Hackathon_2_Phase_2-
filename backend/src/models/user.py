from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List
import uuid


# Handle circular import
if TYPE_CHECKING:
    from .task import Task
    from .conversation import Conversation
    from .message import Message


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    password_hash: str = Field()
    email_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)

    # Relationships
    tasks: Optional[List["Task"]] = Relationship(back_populates="user")
    conversations: Optional[List["Conversation"]] = Relationship(back_populates="user")
    messages: Optional[List["Message"]] = Relationship(back_populates="user")


class UserRead(SQLModel):
    id: uuid.UUID
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    is_active: bool


class UserCreate(SQLModel):
    email: str = Field(min_length=1, max_length=255)
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8, max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)


class UserUpdate(SQLModel):
    email: Optional[str] = Field(default=None, max_length=255)
    username: Optional[str] = Field(default=None, max_length=50)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    password: Optional[str] = Field(default=None, min_length=8, max_length=255)
    email_verified: Optional[bool] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
