from sqlmodel import SQLModel, Field
from typing import Optional
import uuid
from datetime import datetime

# Minimal User model without circular imports
class UserBase(SQLModel):
    email: str = Field(unique=True)
    username: str = Field(unique=True)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    password_hash: str = Field(nullable=False)
    email_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)

print("User model defined successfully!")