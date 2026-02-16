# Claude Code Configuration - Frontend

## Purpose
This file configures the Claude Code workflow specifically for the frontend of the Hackathon-Todo application.

## Frontend Specifications
- **Framework**: React.js with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Redux Toolkit or Zustand
- **Routing**: React Router
- **API Client**: Axios or Fetch API with TypeScript interfaces

## Key Files and Directories
- `src/` - Main source code
- `src/components/` - Reusable UI components
- `src/pages/` - Page-level components
- `src/hooks/` - Custom React hooks
- `src/types/` - TypeScript type definitions
- `src/services/` - API service implementations
- `src/utils/` - Utility functions

## Component Development Guidelines
1. Follow the UI components specification in `../specs/ui/components.md`
2. Implement responsive design according to the specifications
3. Use TypeScript for type safety
4. Follow accessibility best practices (WCAG 2.1 AA)
5. Implement proper error boundaries
6. Use semantic HTML elements

## Page Implementation Guidelines
1. Follow the UI pages specification in `../specs/ui/pages.md`
2. Implement proper routing with React Router
3. Handle loading and error states appropriately
4. Implement proper form validation
5. Follow authentication flow requirements

## API Integration
1. Refer to the REST API endpoints specification in `../specs/api/rest-endpoints.md`
2. Implement proper error handling for API calls
3. Use TypeScript interfaces that match the API response structures
4. Implement caching where appropriate
5. Handle authentication headers automatically

## Code Quality Standards
- Follow React best practices and official recommendations
- Use ESLint and Prettier for code formatting
- Write comprehensive unit tests using Jest and React Testing Library
- Implement integration tests for critical user flows