# Hackathon-Todo Monorepo

This is a full-stack todo application with authentication, built using a monorepo structure.

## Project Structure

```
hackathon-todo/
├── .spec-kit/
│   └── config.yaml
├── specs/                   # Project specifications
│   ├── overview.md
│   ├── architecture.md
│   ├── features/
│   │   ├── task-crud.md
│   │   └── authentication.md
│   ├── api/
│   │   └── rest-endpoints.md
│   ├── database/
│   │   └── schema.md
│   └── ui/
│       ├── components.md
│       └── pages.md
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── contexts/
│   │   ├── types/
│   │   └── styles/
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   └── README.md
├── backend/
│   ├── src/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   ├── middleware/
│   │   ├── database/
│   │   └── utils/
│   ├── requirements.txt
│   ├── alembic.ini
│   └── README.md
├── docker-compose.yml
├── README.md
└── seed.sql
```

## Running the Application

### Prerequisites

- Docker and Docker Compose
- Node.js (for local development)
- Python 3.11+ (for local development)

### Option 1: Using Docker Compose (Recommended)

1. Navigate to the project root directory:
   ```bash
   cd hackathon-todo
   ```

2. Create a `.env` file in the root directory with the following content:
   ```
   POSTGRES_DB=todoapp
   POSTGRES_USER=user
   POSTGRES_PASSWORD=password
   BETTER_AUTH_SECRET=your-super-secret-better-auth-key-here-make-it-long-and-random
   BACKEND_URL=http://localhost:4000/api/v1
   ```

3. Start the services:
   ```bash
   docker-compose up --build
   ```

4. The frontend will be available at `http://localhost:3000`
5. The backend API will be available at `http://localhost:4000`

### Option 2: Running Locally

#### Backend

1. Navigate to the backend directory:
   ```bash
   cd hackathon-todo/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   export DATABASE_URL=postgresql://user:password@localhost:5432/todoapp
   export BETTER_AUTH_SECRET=your-super-secret-better-auth-key-here-make-it-long-and-random
   ```

5. Run the backend:
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

#### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd hackathon-todo/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env.local` file with the following content:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   ```

4. Run the frontend:
   ```bash
   npm run dev
   ```

5. The frontend will be available at `http://localhost:3000`

## Sample Data

The application comes with sample users and tasks pre-seeded in the database:

### Users
- admin@example.com (password: admin123)
- user1@example.com (password: user123)
- user2@example.com (password: user223)

### Tasks
Sample tasks are created for each user to demonstrate the functionality.

## Features

- **Authentication**: Secure login and registration with JWT tokens
- **Task Management**: Full CRUD operations for tasks
- **User Isolation**: Users can only see and modify their own tasks
- **Responsive UI**: Works on desktop, tablet, and mobile devices
- **Professional UI**: Clean, modern interface with TaskCard and TaskForm components
- **API Integration**: Axios client with automatic JWT token attachment
- **Error Handling**: Proper error states and notifications
- **Loading States**: Visual feedback during API operations

## API Endpoints

The backend provides the following API endpoints:

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/tasks` - Get all tasks for authenticated user
- `GET /api/v1/tasks/{id}` - Get a specific task
- `POST /api/v1/tasks` - Create a new task
- `PUT /api/v1/tasks/{id}` - Update a specific task
- `DELETE /api/v1/tasks/{id}` - Delete a specific task
- `PATCH /api/v1/tasks/{id}/status` - Toggle task completion status

All endpoints except login and registration require a valid JWT token in the Authorization header.