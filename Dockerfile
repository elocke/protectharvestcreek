FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"

RUN mkdir -p /app/data

EXPOSE 5111

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5111"]

HEALTHCHECK CMD curl -f http://localhost:5111/healthz || exit 1