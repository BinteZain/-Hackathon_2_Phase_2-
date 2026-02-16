from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List
import uuid


# Handle circular import
if TYPE_CHECKING:
    from .task import Task


class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False, max_length=255)
    username: str = Field(unique=True, nullable=False, max_length=50)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    password_hash: str = Field(nullable=False, max_length=255)
    email_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)

    # Relationship
    tasks: Optional[List["Task"]] = Relationship(back_populates="user")


class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
    is_active: bool