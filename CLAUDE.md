# Claude Code Configuration

## Purpose
This file configures the Claude Code workflow for the Hackathon-Todo monorepo project.

## Project Context
- **Project Name**: Hackathon-Todo
- **Type**: Full-stack Todo application
- **Spec-Kit Version**: 1.0
- **Workflow**: Spec-Kit Plus + Claude Code

## Directory Structure
```
hackathon-todo/
├── .spec-kit/
│   └── config.yaml
├── specs/
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
│   └── CLAUDE.md
├── backend/
│   └── CLAUDE.md
├── docker-compose.yml
└── README.md
```

## Claude Usage Guidelines
1. Always refer to the specifications in the `specs/` directory when implementing features
2. Follow the architecture guidelines outlined in `specs/architecture.md`
3. Implement features according to the detailed requirements in the respective feature specs
4. Maintain consistency with the UI components and pages specifications
5. Ensure API implementations match the endpoint specifications
6. Follow the database schema when implementing data models

## Workflow Integration
- Use Claude to generate code based on the specifications
- Validate implementations against the requirements
- Update specifications as needed during development
- Maintain alignment between frontend and backend implementations