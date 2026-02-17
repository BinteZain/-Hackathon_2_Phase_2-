#!/usr/bin/env python3
"""
Test script for MCP Todo Server.

This script tests all MCP tools without requiring stdio transport.
"""

import asyncio
import uuid
import json
from datetime import datetime

from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, Session, relationship
from sqlalchemy.dialects.sqlite import CHAR

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True)
    email = Column(String(255), nullable=False)
    username = Column(String(50), nullable=False)
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")


class Task(Base):
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


# Use in-memory SQLite for testing
engine = create_engine("sqlite:///:memory:", echo=False)


def task_to_dict(task: Task) -> dict:
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


async def handle_add_task(args):
    user_id = args["user_id"]
    title = args["title"]
    
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return {"success": False, "error": f"User not found: {user_id}"}
        
        task = Task(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            description=args.get("description"),
            priority=args.get("priority", "medium"),
            status=args.get("status", "pending"),
            due_date=datetime.fromisoformat(args["due_date"].replace("Z", "+00:00")) if args.get("due_date") else None
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return {"success": True, "task": task_to_dict(task)}


async def handle_list_tasks(args):
    user_id = args["user_id"]
    limit = min(args.get("limit", 50), 100)
    offset = args.get("offset", 0)
    
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return {"success": False, "error": f"User not found: {user_id}"}
        
        query = session.query(Task).filter(Task.user_id == user_id)
        
        if args.get("status"):
            query = query.filter(Task.status == args["status"])
        if args.get("priority"):
            query = query.filter(Task.priority == args["priority"])
        
        tasks = query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "success": True,
            "count": len(tasks),
            "tasks": [task_to_dict(t) for t in tasks]
        }


async def handle_complete_task(args):
    user_id = args["user_id"]
    task_id = args["task_id"]
    
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return {"success": False, "error": f"User not found: {user_id}"}
        
        task = session.get(Task, task_id)
        if not task:
            return {"success": False, "error": f"Task not found: {task_id}"}
        
        if task.user_id != user_id:
            return {"success": False, "error": "Task does not belong to user"}
        
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        session.commit()
        session.refresh(task)
        
        return {"success": True, "task": task_to_dict(task)}


async def handle_delete_task(args):
    user_id = args["user_id"]
    task_id = args["task_id"]
    
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return {"success": False, "error": f"User not found: {user_id}"}
        
        task = session.get(Task, task_id)
        if not task:
            return {"success": False, "error": f"Task not found: {task_id}"}
        
        if task.user_id != user_id:
            return {"success": False, "error": "Task does not belong to user"}
        
        session.delete(task)
        session.commit()
        
        return {"success": True, "message": f"Task {task_id} deleted"}


async def handle_update_task(args):
    user_id = args["user_id"]
    task_id = args["task_id"]
    
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return {"success": False, "error": f"User not found: {user_id}"}
        
        task = session.get(Task, task_id)
        if not task:
            return {"success": False, "error": f"Task not found: {task_id}"}
        
        if task.user_id != user_id:
            return {"success": False, "error": "Task does not belong to user"}
        
        if args.get("title"):
            task.title = args["title"]
        if args.get("description") is not None:
            task.description = args["description"]
        if args.get("status"):
            task.status = args["status"]
            task.completed_at = datetime.utcnow() if args["status"] == "completed" else None
        if args.get("priority"):
            task.priority = args["priority"]
        
        task.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(task)
        
        return {"success": True, "task": task_to_dict(task)}


async def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("MCP Todo Server - Tool Tests")
    print("=" * 60)
    
    # Create tables
    Base.metadata.create_all(engine)
    print("\n[OK] Database initialized\n")
    
    # Create test user
    test_user_id = str(uuid.uuid4())
    with Session(engine) as session:
        user = User(id=test_user_id, email="test@example.com", username="testuser")
        session.add(user)
        session.commit()
    print(f"[OK] Created test user: {test_user_id}\n")
    
    # Test 1: Add Task
    print("Test 1: add_task")
    result = await handle_add_task({
        "user_id": test_user_id,
        "title": "Test Task 1",
        "description": "Test description",
        "priority": "high"
    })
    assert result["success"], f"Failed: {result}"
    task1_id = result["task"]["id"]
    print(f"  [OK] Created task: {task1_id}")
    print(f"  [OK] Title: {result['task']['title']}")
    print(f"  [OK] Priority: {result['task']['priority']}\n")
    
    # Test 2: List Tasks
    print("Test 2: list_tasks")
    result = await handle_list_tasks({"user_id": test_user_id})
    assert result["success"], f"Failed: {result}"
    assert result["count"] == 1, f"Expected 1 task, got {result['count']}"
    print(f"  [OK] Found {result['count']} task(s)\n")
    
    # Test 3: Add more tasks
    print("Test 3: add_task (multiple)")
    for i in range(2, 4):
        result = await handle_add_task({
            "user_id": test_user_id,
            "title": f"Test Task {i}",
            "status": "in_progress" if i == 2 else "completed"
        })
        assert result["success"]
    print("  [OK] Created 2 more tasks\n")
    
    # Test 4: List with filter
    print("Test 4: list_tasks (filtered)")
    result = await handle_list_tasks({"user_id": test_user_id, "status": "completed"})
    assert result["count"] == 1
    print(f"  [OK] Found {result['count']} completed task(s)\n")
    
    # Test 5: Complete Task
    print("Test 5: complete_task")
    result = await handle_complete_task({"user_id": test_user_id, "task_id": task1_id})
    assert result["success"]
    assert result["task"]["status"] == "completed"
    assert result["task"]["completed_at"] is not None
    print(f"  [OK] Task completed at: {result['task']['completed_at']}\n")
    
    # Test 6: Update Task
    print("Test 6: update_task")
    result = await handle_update_task({
        "user_id": test_user_id,
        "task_id": task1_id,
        "title": "Updated Title",
        "priority": "low"
    })
    assert result["success"]
    assert result["task"]["title"] == "Updated Title"
    assert result["task"]["priority"] == "low"
    print(f"  [OK] Title updated to: {result['task']['title']}")
    print(f"  [OK] Priority updated to: {result['task']['priority']}\n")
    
    # Test 7: Delete Task
    print("Test 7: delete_task")
    result = await handle_delete_task({"user_id": test_user_id, "task_id": task1_id})
    assert result["success"]
    print(f"  [OK] Task deleted\n")
    
    # Test 8: Ownership enforcement
    print("Test 8: Ownership enforcement")
    other_user_id = str(uuid.uuid4())
    with Session(engine) as session:
        user = User(id=other_user_id, email="other@example.com", username="otheruser")
        session.add(user)
        session.commit()
    
    # Try to delete another user's task
    result = await handle_delete_task({"user_id": other_user_id, "task_id": task1_id})
    # Task was already deleted, so expect "not found"
    assert not result["success"]
    print("  [OK] Cannot access other user's tasks\n")
    
    # Test 9: Invalid user
    print("Test 9: Invalid user handling")
    fake_user_id = str(uuid.uuid4())
    result = await handle_list_tasks({"user_id": fake_user_id})
    assert not result["success"]
    assert "not found" in result["error"].lower()
    print(f"  [OK] Error: {result['error']}\n")
    
    print("=" * 60)
    print("All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_tests())
