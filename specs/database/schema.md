# Database Schema Specification

## Overview
This document defines the database schema for the Hackathon-Todo application.

## Tables

### Users Table
```
users
- id (UUID, Primary Key, Default: gen_random_uuid())
- email (VARCHAR(255), UNIQUE, NOT NULL)
- username (VARCHAR(50), UNIQUE, NOT NULL)
- password_hash (VARCHAR(255), NOT NULL)
- first_name (VARCHAR(100))
- last_name (VARCHAR(100))
- avatar_url (TEXT)
- email_verified (BOOLEAN, DEFAULT: false)
- email_verification_token (VARCHAR(255))  -- For email verification
- password_reset_token (VARCHAR(255))      -- For password resets
- password_reset_expires (TIMESTAMP)       -- Expiration for reset tokens
- created_at (TIMESTAMP, DEFAULT: NOW())
- updated_at (TIMESTAMP, DEFAULT: NOW())
- last_login_at (TIMESTAMP)
- is_active (BOOLEAN, DEFAULT: true)
```

### Tasks Table
```
tasks
- id (UUID, Primary Key, Default: gen_random_uuid())
- user_id (UUID, Foreign Key -> users.id, NOT NULL)
- title (VARCHAR(255), NOT NULL)
- description (TEXT)
- status (VARCHAR(20), CHECK: 'pending', 'in-progress', 'completed', DEFAULT: 'pending')
- priority (VARCHAR(10), CHECK: 'low', 'medium', 'high', DEFAULT: 'medium')
- due_date (TIMESTAMP)
- completed_at (TIMESTAMP)
- created_at (TIMESTAMP, DEFAULT: NOW())
- updated_at (TIMESTAMP, DEFAULT: NOW())
```

### Projects Table (Optional)
```
projects
- id (UUID, Primary Key, Default: gen_random_uuid())
- user_id (UUID, Foreign Key -> users.id, NOT NULL)
- name (VARCHAR(255), NOT NULL)
- description (TEXT)
- color (VARCHAR(7))  -- Hex color code for UI
- created_at (TIMESTAMP, DEFAULT: NOW())
- updated_at (TIMESTAMP, DEFAULT: NOW())
```

### Sessions Table (For JWT management)
```
sessions
- id (UUID, Primary Key, Default: gen_random_uuid())
- user_id (UUID, Foreign Key -> users.id, NOT NULL)
- token (TEXT, NOT NULL)  -- Refresh token
- expires_at (TIMESTAMP, NOT NULL)
- created_at (TIMESTAMP, DEFAULT: NOW())
- is_revoked (BOOLEAN, DEFAULT: false)
```

## Indexes
- Index on users.email for quick lookups
- Index on users.username for quick lookups
- Index on tasks.user_id for filtering tasks by user
- Index on tasks.status for filtering by status
- Index on tasks.due_date for sorting by due date
- Index on sessions.token for quick session validation
- Composite index on sessions.user_id and is_revoked for active session queries

## Relationships
- Users to Tasks: One-to-Many (One user can have many tasks)
- Users to Projects: One-to-Many (One user can have many projects)
- Users to Sessions: One-to-Many (One user can have many sessions)
- Projects to Tasks: One-to-Many (One project can have many tasks) - optional relation

## Constraints
- Users must have a unique email and username
- Tasks must belong to a valid user
- Tasks must have a title
- Tasks status must be one of the allowed values
- Tasks priority must be one of the allowed values
- Sessions must belong to a valid user
- Sessions must have an expiration date