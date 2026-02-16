from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class SimpleTask(SQLModel):
    title: str
    description: Optional[str] = None


print("Simple model definition works")