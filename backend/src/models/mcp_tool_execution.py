from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, Any
from sqlalchemy import JSON, Column

# Handle circular import
if TYPE_CHECKING:
    from .message import Message


class MCPToolExecution(SQLModel, table=True):
    __tablename__ = "mcp_tool_executions"

    id: int = Field(primary_key=True)
    message_id: int = Field(foreign_key="messages.id", index=True)
    tool_name: str = Field()
    tool_args: Dict[str, Any] = Field(default_factory=dict, sa_column=Column("tool_args", JSON))
    tool_result: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column("tool_result", JSON))
    status: str = Field()
    error_message: Optional[str] = Field(default=None)
    executed_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    message: Optional["Message"] = Relationship(back_populates="tool_executions")


class MCPToolExecutionRead(SQLModel):
    id: int
    message_id: int
    tool_name: str
    tool_args: Dict[str, Any]
    tool_result: Optional[Dict[str, Any]] = None
    status: str
    error_message: Optional[str] = None
    executed_at: datetime


class MCPToolExecutionCreate(SQLModel):
    tool_name: str = Field()
    tool_args: Dict[str, Any] = Field(default_factory=dict)
    tool_result: Optional[Dict[str, Any]] = Field(default=None)
    status: str = Field()
    error_message: Optional[str] = Field(default=None)
