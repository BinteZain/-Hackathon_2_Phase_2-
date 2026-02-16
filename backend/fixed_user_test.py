from sqlmodel import SQLModel, Field
from typing import Optional
import uuid
from datetime import datetime

# User model without Field() in base class
class UserBase(SQLModel):
    email: str  # No Field() here
    username: str  # No Field() here
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True)  # Field() with constraints in the table class
    username: str = Field(unique=True)  # Field() with constraints in the table class
    password_hash: str = Field(nullable=False)
    email_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)

print("User model defined successfully!")