# Backend Dockerfile
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first for caching
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system -e ".[dev]"

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "upskills"]
