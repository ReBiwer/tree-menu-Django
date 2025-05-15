FROM python:3.12-slim

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.5.22 /uv /bin/uv

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen --no-dev

COPY . .

CMD ["ls", "-a"]
CMD ["python", "app/manage.py", "runserver", "0.0.0.0:8000"]