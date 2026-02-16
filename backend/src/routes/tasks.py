from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from ..database.session import get_session
from ..models.task import Task, TaskCreate, TaskUpdate
from ..schemas.task import TaskRead, TaskCreate as TaskCreateSchema, TaskUpdate as TaskUpdateSchema, ApiResponse, TaskToggleComplete
from ..utils.jwt import get_current_user, TokenData
from datetime import datetime
import uuid

router = APIRouter()


@router.get("/tasks", response_model=ApiResponse)
def get_tasks(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all tasks for the authenticated user
    """
    try:
        # Convert user_id from string to UUID
        user_id = uuid.UUID(current_user.user_id)
        
        # Query tasks for the current user (enforcing ownership)
        statement = select(Task).where(Task.user_id == user_id)
        tasks = session.exec(statement).all()
        
        # Convert SQLModel objects to Pydantic objects
        task_list = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "completed_at": task.completed_at
            }
            task_list.append(TaskRead(**task_dict))
        
        return ApiResponse(
            success=True,
            data={"tasks": task_list},
            message="Tasks retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving tasks: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=ApiResponse)
def get_task(
    task_id: uuid.UUID,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific task by ID
    """
    try:
        user_id = uuid.UUID(current_user.user_id)
        
        # Query task for the current user (enforcing ownership)
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or does not belong to the authenticated user"
            )
        
        # Convert SQLModel object to Pydantic object
        task_dict = {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "completed_at": task.completed_at
        }
        
        return ApiResponse(
            success=True,
            data={"task": TaskRead(**task_dict)},
            message="Task retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the task: {str(e)}"
        )


@router.post("/tasks", response_model=ApiResponse)
def create_task(
    task_create: TaskCreateSchema,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task
    """
    try:
        user_id = uuid.UUID(current_user.user_id)
        
        # Create task object with authenticated user's ID (enforcing ownership)
        task = Task(
            **task_create.model_dump(),
            user_id=user_id
        )
        
        session.add(task)
        session.commit()
        session.refresh(task)
        
        # Convert SQLModel object to Pydantic object
        task_dict = {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "completed_at": task.completed_at
        }
        
        return ApiResponse(
            success=True,
            data={"task": TaskRead(**task_dict)},
            message="Task created successfully"
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the task: {str(e)}"
        )


@router.put("/tasks/{task_id}", response_model=ApiResponse)
def update_task(
    task_id: uuid.UUID,
    task_update: TaskUpdateSchema,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a specific task
    """
    try:
        user_id = uuid.UUID(current_user.user_id)
        
        # Find the task for the current user (enforcing ownership)
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or does not belong to the authenticated user"
            )
        
        # Update task with provided values
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        # Update the updated_at timestamp
        task.updated_at = datetime.utcnow()
        
        session.add(task)
        session.commit()
        session.refresh(task)
        
        # Convert SQLModel object to Pydantic object
        task_dict = {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "completed_at": task.completed_at
        }
        
        return ApiResponse(
            success=True,
            data={"task": TaskRead(**task_dict)},
            message="Task updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the task: {str(e)}"
        )


@router.delete("/tasks/{task_id}", response_model=ApiResponse)
def delete_task(
    task_id: uuid.UUID,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific task
    """
    try:
        user_id = uuid.UUID(current_user.user_id)
        
        # Find the task for the current user (enforcing ownership)
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or does not belong to the authenticated user"
            )
        
        session.delete(task)
        session.commit()
        
        return ApiResponse(
            success=True,
            message="Task deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the task: {str(e)}"
        )


@router.patch("/tasks/{task_id}/status", response_model=ApiResponse)
def toggle_task_completion(
    task_id: uuid.UUID,
    toggle_data: TaskToggleComplete,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle task completion status
    """
    try:
        user_id = uuid.UUID(current_user.user_id)
        
        # Find the task for the current user (enforcing ownership)
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or does not belong to the authenticated user"
            )
        
        # Update completion status
        if toggle_data.completed:
            task.status = "completed"
            task.completed_at = datetime.utcnow()
        else:
            task.status = "pending"
            task.completed_at = None
        
        # Update the updated_at timestamp
        task.updated_at = datetime.utcnow()
        
        session.add(task)
        session.commit()
        session.refresh(task)
        
        # Convert SQLModel object to Pydantic object
        task_dict = {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "completed_at": task.completed_at
        }
        
        return ApiResponse(
            success=True,
            data={"task": TaskRead(**task_dict)},
            message=f"Task {'marked as completed' if toggle_data.completed else 'marked as pending'}"
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating task status: {str(e)}"
        )