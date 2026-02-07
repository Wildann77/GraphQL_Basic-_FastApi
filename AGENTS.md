# Agent Guidelines for GraphQL Basic API

This document provides guidelines for AI agents working in this repository.

## Build / Lint / Test Commands

### Development Commands
```bash
# Install dependencies
make install              # Production dependencies
make dev-install          # Dev dependencies + pre-commit hooks

# Docker operations
make up                   # Start services (detached)
make watch               # Start with hot reload (watch mode)
make down                # Stop services and remove volumes
make logs                # View API logs

# Testing
make test                 # Run all tests with verbose output
make test-cov            # Run tests with coverage report
pytest tests/test_users.py -v                    # Run single test file
pytest tests/test_users.py::test_create_user -v  # Run single test
pytest tests/ -k "test_create" -v                # Run tests matching pattern

# Code Quality
make lint                 # Run ruff check and mypy
make format               # Run black and ruff --fix
ruff check src --fix      # Auto-fix linting issues
mypy src                  # Type checking only

# Database Migrations
make migrate m="description"   # Create new migration
make migrate-up                # Apply all migrations
make migrate-down              # Rollback one migration
```

## Code Style Guidelines

### Imports
- Group imports in this order: stdlib, third-party, local (with blank lines between)
- Use absolute imports: `from src.features.users.schemas import User`
- Sort imports with ruff (configured to handle automatically)
- Example:
  ```python
  from contextlib import asynccontextmanager
  from typing import Optional

  import strawberry
  from fastapi import FastAPI
  from strawberry.types import Info

  from src.config import settings
  from src.core.logging import logger
  ```

### Formatting
- Line length: 88 characters (Black default)
- Target Python version: 3.11+
- Use Black for code formatting
- Use double quotes for strings
- Trailing commas in multi-line structures

### Types & Naming
- **Functions**: `snake_case` - `async def get_user(user_id: int)`
- **Classes**: `PascalCase` - `class UserService`, `class CreateUserInput`
- **Constants**: `UPPER_SNAKE_CASE` - `DATABASE_URL`, `CACHE_TTL`
- **Variables**: `snake_case` - `user_id`, `is_active`
- **Private**: Prefix with underscore `_internal_method()`
- **Type hints**: Required for function parameters and return types
- Use `Optional[T]` or `T | None` for nullable types

### Project Structure
```
src/
├── core/                 # Shared infrastructure
│   ├── base.py          # SQLAlchemy base classes
│   ├── cache.py         # Redis caching
│   ├── database.py      # DB connection/session
│   ├── dataloaders.py   # GraphQL DataLoaders
│   ├── exceptions.py    # Error types
│   ├── logging.py       # Structured logging
│   └── security.py      # Auth & rate limiting
├── features/            # Feature modules
│   └── users/           # User domain
│       ├── graphql.py   # GraphQL resolvers
│       ├── models.py    # SQLAlchemy models
│       ├── repository.py # Data access layer
│       ├── schemas.py   # Pydantic/Strawberry types
│       └── service.py   # Business logic
├── config.py           # Pydantic settings
└── main.py             # FastAPI app factory
```

### Error Handling
- Use custom exceptions from `src.core.exceptions`:
  - `ValidationError` - Input validation failures
  - `NotFoundError` - Resource not found
  - `DatabaseError` - Database operation failures
  - `AuthenticationError` - Auth failures
- Always log exceptions with `logger.error("context", error=str(e))`
- Handle exceptions at GraphQL resolver level
- Use Union types for error responses: `UserResponse = Union[User, UserNotFoundError, ValidationError]`
- Use `assert` for type narrowing in schema conversion methods

### Database & GraphQL Patterns
- Use Repository pattern for data access
- Use Service layer for business logic
- Use DataLoaders for N+1 query prevention
- Implement soft delete with `SoftDeleteMixin`
- Pydantic for validation, Strawberry for GraphQL types
- Always commit/rollback transactions explicitly
- Clear cache after mutations with pattern matching

### Logging
- Use structured logging: `logger.info("event_name", key=value)`
- Include context: request_id, user_id where relevant
- Log errors with full context

### Testing
- Use `pytest` with `pytest-asyncio`
- Use `AsyncClient` from `httpx` for API tests
- Tests should be in `tests/` directory with `test_*.py` naming
- Use fixtures for shared resources
- Test file should match pattern: `test_<feature>.py`

### Configuration
- All settings in `src/config.py` using Pydantic Settings
- Environment variables loaded from `.env` file
- Access via `settings.CONSTANT_NAME`

### Comments
- Use docstrings for modules, classes, and public methods
- Keep comments minimal; prefer clear code
- Comments in Indonesian are acceptable (existing codebase pattern)

## Pre-commit Checks
Always run before committing:
```bash
make lint
make test
```

## Environment
- Python 3.11+
- Docker Compose for local development
- MySQL 8.0 + Redis 7 required for full stack
