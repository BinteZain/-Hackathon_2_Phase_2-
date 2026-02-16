# REST API Endpoints Specification

## Base URL
All API endpoints are prefixed with `/api/v1`

## Authentication
Most endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Common Response Format
Successful responses follow this format:
```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation successful"
}
```

Error responses follow this format:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

## Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Authenticate user and return token
- `POST /auth/logout` - Log out user
- `POST /auth/refresh` - Refresh access token
- `POST /auth/forgot-password` - Initiate password reset
- `POST /auth/reset-password` - Complete password reset
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update user profile

### Tasks
- `GET /tasks` - Get all tasks for the authenticated user
- `GET /tasks/:id` - Get a specific task
- `POST /tasks` - Create a new task
- `PUT /tasks/:id` - Update a specific task
- `DELETE /tasks/:id` - Delete a specific task
- `PATCH /tasks/:id/status` - Update task status

### Projects/Categories (Optional)
- `GET /projects` - Get all projects for the authenticated user
- `GET /projects/:id` - Get a specific project
- `POST /projects` - Create a new project
- `PUT /projects/:id` - Update a specific project
- `DELETE /projects/:id` - Delete a specific project

## HTTP Status Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource doesn't exist
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error