"""
MCP Server for Todo App - Task Management Tools

This module implements an MCP server that exposes task management tools:
- add_task: Create a new task
- list_tasks: List all tasks for a user
- complete_task: Mark a task as complete
- delete_task: Delete a task
- update_task: Update task details

Each tool enforces task ownership by requiring user_id and verifying it matches.
"""

import asyncio
import uuid
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from sqlalchemy import (
    create_engine, Column, String, DateTime, ForeignKey, select, update, delete
)
from sqlalchemy.orm import declarative_base, Session, relationship
from sqlalchemy.dialects.sqlite import CHAR

Base = declarative_base()


# ============================================================================
# SQLAlchemy Models
# ============================================================================

class User(Base):
    """User table model."""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    email = Column(String(255), nullable=False)
    username = Column(String(50), nullable=False)
    
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")


class Task(Base):
    """Task table model."""
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(String(20), default="pending")
    priority = Column(String(20), default="medium")
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="tasks")


# ============================================================================
# Database Setup
# ============================================================================

from src.database.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(engine)


# ============================================================================
# Response Models
# ============================================================================

def task_to_dict(task: Task) -> dict:
    """Convert Task to dictionary for JSON response."""
    return {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None
    }


# ============================================================================
# MCP Server
# ============================================================================

server = Server("todo-app")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="add_task",
            description="Create a new task for a user. Requires user_id and title. Optional: description, priority, status, due_date.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The UUID of the user who owns the task"
                    },
                    "title": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 255,
                        "description": "The task title"
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 500,
                        "description": "Optional task description"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "default": "medium",
                        "description": "Task priority level"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "default": "pending",
                        "description": "Initial task status"
                    },
                    "due_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Optional due date in ISO format"
                    }
                },
                "required": ["user_id", "title"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List all tasks for a user. Supports filtering by status and priority.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The UUID of the user whose tasks to list"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "Filter by status"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Filter by priority"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 50,
                        "minimum": 1,
                        "maximum": 100,
                        "description": "Maximum number of tasks to return"
                    },
                    "offset": {
                        "type": "integer",
                        "default": 0,
                        "minimum": 0,
                        "description": "Number of tasks to skip"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed. Requires user_id and task_id. Only completes if user owns the task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The UUID of the user who owns the task"
                    },
                    "task_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The UUID of the task to complete"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        ),
        Tool(
            name="delete_task",
            description="Delete a task. Requires user_id and task_id. Only deletes if user owns the task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The UUID of the user who owns the task"
                    },
                    "task_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The UUID of the task to delete"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        ),
        Tool(
            name="update_task",
            description="Update task details. Requires user_id and task_id. Optional: title, description, status, priority, due_date. Only updates if user owns the task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The UUID of the user who owns the task"
                    },
                    "task_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The UUID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 255,
                        "description": "New task title"
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 500,
                        "description": "New task description"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "New task status"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "New task priority"
                    },
                    "due_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "New due date in ISO format"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "add_task":
            return await handle_add_task(arguments)
        elif name == "list_tasks":
            return await handle_list_tasks(arguments)
        elif name == "complete_task":
            return await handle_complete_task(arguments)
        elif name == "delete_task":
            return await handle_delete_task(arguments)
        elif name == "update_task":
            return await handle_update_task(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2))]


async def handle_add_task(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle add_task tool call."""
    user_id = arguments.get("user_id")
    title = arguments.get("title")
    description = arguments.get("description")
    priority = arguments.get("priority", "medium")
    status = arguments.get("status", "pending")
    due_date_str = arguments.get("due_date")

    if not user_id or not title:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": "user_id and title are required"
        }, indent=2))]

    try:
        user_uuid = uuid.UUID(user_id)
        task_uuid = uuid.uuid4()
    except ValueError:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": f"Invalid user_id format: {user_id}"
        }, indent=2))]

    due_date = None
    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
        except ValueError:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"Invalid due_date format: {due_date_str}. Use ISO format."
            }, indent=2))]

    with Session(engine) as session:
        # Verify user exists
        user = session.get(User, str(user_uuid))
        if not user:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"User not found: {user_id}"
            }, indent=2))]

        task = Task(
            id=str(task_uuid),
            user_id=str(user_uuid),
            title=title,
            description=description,
            priority=priority,
            status=status,
            due_date=due_date
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        return [TextContent(type="text", text=json.dumps({
            "success": True,
            "task": task_to_dict(task)
        }, indent=2))]


async def handle_list_tasks(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle list_tasks tool call."""
    user_id = arguments.get("user_id")
    status = arguments.get("status")
    priority = arguments.get("priority")
    limit = min(arguments.get("limit", 50), 100)
    offset = arguments.get("offset", 0)

    if not user_id:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": "user_id is required"
        }, indent=2))]

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": f"Invalid user_id format: {user_id}"
        }, indent=2))]

    with Session(engine) as session:
        # Verify user exists
        user = session.get(User, str(user_uuid))
        if not user:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"User not found: {user_id}"
            }, indent=2))]

        # Build query with ownership enforcement
        query = select(Task).where(Task.user_id == str(user_uuid))

        if status:
            query = query.where(Task.status == status)
        if priority:
            query = query.where(Task.priority == priority)

        query = query.order_by(Task.created_at.desc())
        query = query.offset(offset).limit(limit)

        tasks = session.execute(query).scalars().all()

        return [TextContent(type="text", text=json.dumps({
            "success": True,
            "count": len(tasks),
            "limit": limit,
            "offset": offset,
            "tasks": [task_to_dict(t) for t in tasks]
        }, indent=2))]


async def handle_complete_task(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle complete_task tool call."""
    user_id = arguments.get("user_id")
    task_id = arguments.get("task_id")

    if not user_id or not task_id:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": "user_id and task_id are required"
        }, indent=2))]

    try:
        user_uuid = uuid.UUID(user_id)
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": "Invalid UUID format"
        }, indent=2))]

    with Session(engine) as session:
        # Verify user exists
        user = session.get(User, str(user_uuid))
        if not user:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"User not found: {user_id}"
            }, indent=2))]

        # Get task and verify ownership
        task = session.get(Task, str(task_uuid))
        if not task:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"Task not found: {task_id}"
            }, indent=2))]

        if task.user_id != str(user_uuid):
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "Task does not belong to the specified user"
            }, indent=2))]

        # Update task
        task.status = "completed"
        task.completed_at = datetime.now(timezone.utc)
        task.updated_at = datetime.now(timezone.utc)
        session.add(task)
        session.commit()
        session.refresh(task)

        return [TextContent(type="text", text=json.dumps({
            "success": True,
            "message": "Task marked as completed",
            "task": task_to_dict(task)
        }, indent=2))]


async def handle_delete_task(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle delete_task tool call."""
    user_id = arguments.get("user_id")
    task_id = arguments.get("task_id")

    if not user_id or not task_id:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": "user_id and task_id are required"
        }, indent=2))]

    try:
        user_uuid = uuid.UUID(user_id)
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": "Invalid UUID format"
        }, indent=2))]

    with Session(engine) as session:
        # Verify user exists
        user = session.get(User, str(user_uuid))
        if not user:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"User not found: {user_id}"
            }, indent=2))]

        # Get task and verify ownership
        task = session.get(Task, str(task_uuid))
        if not task:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"Task not found: {task_id}"
            }, indent=2))]

        if task.user_id != str(user_uuid):
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "Task does not belong to the specified user"
            }, indent=2))]

        # Delete task
        session.delete(task)
        session.commit()

        return [TextContent(type="text", text=json.dumps({
            "success": True,
            "message": f"Task {task_id} deleted successfully"
        }, indent=2))]


async def handle_update_task(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle update_task tool call."""
    user_id = arguments.get("user_id")
    task_id = arguments.get("task_id")
    title = arguments.get("title")
    description = arguments.get("description")
    status = arguments.get("status")
    priority = arguments.get("priority")
    due_date_str = arguments.get("due_date")

    if not user_id or not task_id:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": "user_id and task_id are required"
        }, indent=2))]

    try:
        user_uuid = uuid.UUID(user_id)
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": "Invalid UUID format"
        }, indent=2))]

    due_date = None
    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
        except ValueError:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"Invalid due_date format: {due_date_str}. Use ISO format."
            }, indent=2))]

    with Session(engine) as session:
        # Verify user exists
        user = session.get(User, str(user_uuid))
        if not user:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"User not found: {user_id}"
            }, indent=2))]

        # Get task and verify ownership
        task = session.get(Task, str(task_uuid))
        if not task:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"Task not found: {task_id}"
            }, indent=2))]

        if task.user_id != str(user_uuid):
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "Task does not belong to the specified user"
            }, indent=2))]

        # Update fields
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
            if status == "completed":
                task.completed_at = datetime.utcnow()
            else:
                task.completed_at = None
        if priority is not None:
            task.priority = priority
        if due_date is not None:
            task.due_date = due_date

        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

        return [TextContent(type="text", text=json.dumps({
            "success": True,
            "message": "Task updated successfully",
            "task": task_to_dict(task)
        }, indent=2))]


# ============================================================================
# Server Entry Point
# ============================================================================

async def main():
    """Run the MCP server."""
    # Initialize database
    init_db()
    
    print("MCP Todo Server starting...", flush=True)

    # Run server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
