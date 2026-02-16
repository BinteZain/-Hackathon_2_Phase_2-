# Claude Code Configuration - Backend

## Purpose
This file configures the Claude Code workflow specifically for the backend of the Hackathon-Todo application.

## Backend Specifications
- **Runtime**: Node.js with TypeScript
- **Framework**: Express.js
- **Database**: PostgreSQL or MongoDB
- **Authentication**: JWT with refresh tokens
- **Validation**: Joi or express-validator
- **Testing**: Jest for unit tests, Supertest for API tests

## Key Files and Directories
- `src/` - Main source code
- `src/routes/` - API route definitions
- `src/controllers/` - Request handling logic
- `src/models/` - Data models and schemas
- `src/middleware/` - Custom middleware functions
- `src/services/` - Business logic implementations
- `src/utils/` - Utility functions
- `src/config/` - Configuration files

## API Development Guidelines
1. Follow the REST API endpoints specification in `../specs/api/rest-endpoints.md`
2. Implement proper request validation using middleware
3. Use TypeScript for type safety throughout
4. Implement proper error handling and logging
5. Follow security best practices (input sanitization, rate limiting, etc.)

## Database Implementation Guidelines
1. Follow the database schema specification in `../specs/database/schema.md`
2. Implement proper data validation at the model level
3. Use parameterized queries to prevent SQL injection
4. Implement proper indexing based on query patterns
5. Handle database transactions appropriately

## Authentication Implementation
1. Follow the authentication features specification in `../specs/features/authentication.md`
2. Implement secure password hashing using bcrypt
3. Properly manage JWT tokens with refresh token rotation
4. Implement proper session management
5. Follow OWASP security guidelines

## Code Quality Standards
- Follow Express.js best practices and security guidelines
- Use ESLint and Prettier for code formatting
- Write comprehensive unit and integration tests
- Implement proper logging for debugging and monitoring
- Document API endpoints using Swagger/OpenAPI