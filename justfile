# protectharvestcreek development commands

set dotenv-load

# List available commands
default:
    @just --list

# Run dev server with hot reload
dev:
    uv run uvicorn app:app --host 0.0.0.0 --port 5111 --reload

# Run dev server (no reload)
run:
    uv run python app.py

# Build and run docker stack locally (caddy on :5111)
up *ARGS:
    docker compose up --build {{ARGS}}

# Stop docker stack
down:
    docker compose down

# Rebuild and restart the full stack (no cache)
rebuild:
    docker compose down
    docker compose up --build --force-recreate -d

# Run production stack (no port exposure, tunnel only)
prod *ARGS:
    docker compose -f compose.yaml up --build {{ARGS}}

# Install dependencies
install:
    uv sync

# Add a dependency
add *PACKAGES:
    uv add {{PACKAGES}}

# Lint with ruff
lint:
    uv run ruff check .

# Lint and fix
lint-fix:
    uv run ruff check --fix .

# Format with ruff
fmt:
    uv run ruff format .

# Check formatting without changing files
fmt-check:
    uv run ruff format --check .

# Run all checks (lint + format check)
check: lint fmt-check

# Fix all auto-fixable issues
fix: lint-fix fmt

# Reset comment counter
reset-counter:
    echo "0" > data/counter.txt
