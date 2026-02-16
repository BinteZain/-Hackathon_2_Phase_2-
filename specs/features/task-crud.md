# Task CRUD Features Specification

## Overview
This document outlines the requirements for the core Task/To-do CRUD functionality of the application.

## Features

### 1. Create Task
- Users can create new tasks with title and description
- Optional due date and priority level
- Assign tasks to specific projects/categories
- Validation for required fields

### 2. Read Tasks
- View all tasks assigned to the user
- Filter tasks by status (pending, in-progress, completed)
- Sort tasks by creation date, due date, or priority
- Search functionality by task title or description

### 3. Update Task
- Modify task title, description, due date, and priority
- Change task status (to-do, in-progress, done)
- Reassign tasks to different projects/categories
- Track task modification history

### 4. Delete Task
- Soft delete with trash bin functionality
- Permanent deletion after retention period
- Confirmation dialog before deletion

## User Interface Requirements
- Intuitive form for creating/editing tasks
- Visual indicators for task status and priority
- Drag-and-drop functionality for reordering tasks
- Responsive design for all device sizes

## API Endpoints
- POST /api/tasks - Create a new task
- GET /api/tasks - Retrieve all tasks for the user
- GET /api/tasks/:id - Retrieve a specific task
- PUT /api/tasks/:id - Update a specific task
- DELETE /api/tasks/:id - Delete a specific task

## Validation Rules
- Title is required (min 1 character, max 100 characters)
- Description is optional (max 500 characters)
- Due date must be in the future if provided
- Priority must be one of: low, medium, high