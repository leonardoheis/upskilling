# UpSkills Backend

FastAPI backend for the UpSkills career development platform.

## Quick Start

```bash
# Sync dependencies
uv sync

# Run development server
uv run poe serve-dev
```

API documentation available at http://localhost:8000/docs

## Project Structure

```
src/upskills/
├── api/routers/      # FastAPI route handlers
├── core/             # Config, security, dependencies
├── db/               # Database provider abstraction
├── models/
│   ├── db/           # SQLAlchemy ORM models
│   └── domain/       # Pydantic request/response models
├── repositories/     # Data access layer
├── services/         # Business logic layer
├── containers.py     # DI container
└── main.py           # FastAPI app entry point
```

## Available Commands

```bash
uv run poe serve        # Run production server
uv run poe serve-dev    # Run dev server with hot reload
uv run poe test         # Run tests
uv run poe format       # Run pre-commit formatters
uv run poe lint         # Run ruff linter
uv run poe typecheck    # Run mypy type checker
```
