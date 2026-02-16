# Hackathon-Todo Backend

This is the backend service for the Hackathon-Todo application, built with FastAPI and SQLModel.

## Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon)
- **Authentication**: JWT with BETTER_AUTH_SECRET
- **Serialization**: Pydantic

## Features

- Full CRUD operations for tasks
- JWT-based authentication and authorization
- User isolation (users can only access their own tasks)
- Comprehensive API endpoints as specified
- Pydantic models for request/response validation
- Timestamps for all records (created_at, updated_at)

## API Endpoints

The API follows the specification in `specs/api/rest-endpoints.md`:

- `GET /api/v1/tasks` - Get all tasks for the authenticated user
- `GET /api/v1/tasks/{id}` - Get a specific task
- `POST /api/v1/tasks` - Create a new task
- `PUT /api/v1/tasks/{id}` - Update a specific task
- `DELETE /api/v1/tasks/{id}` - Delete a specific task
- `PATCH /api/v1/tasks/{id}/status` - Toggle task completion status

## Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/todoapp

# Better Auth Configuration
BETTER_AUTH_SECRET=your-better-auth-secret-key
```

## Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables (copy `.env.example` to `.env` and update values)

3. Run the application:
   ```bash
   uvicorn src.main:app --reload
   ```

The API will be available at `http://localhost:8000`.

## Running with Docker

Build and run the container:

```bash
docker build -t hackathon-todo-backend .
docker run -p 4000:4000 hackathon-todo-backend
```

Or use with the provided docker-compose.yml in the root directory.