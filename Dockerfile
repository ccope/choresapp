FROM python:3.14-slim-trixie AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1

WORKDIR /app
RUN apt update && apt install -y libsqlite3-0

FROM base AS builder
RUN apt update && apt install -y gcc libffi-dev g++ git

ENV PYTHONHASHSEED=0 \
  PIP_DEFAULT_TIMEOUT=100 \
  PIP_DISABLE_PIP_VERSION_CHECK=1

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --locked --no-install-project

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
RUN mkdir -p /app/data && chown www-data:www-data /app/data

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Run the FastAPI application by default
# Uses `uv run` to sync dependencies on startup, respecting UV_NO_DEV
# Uses `fastapi dev` to enable hot-reloading when the `watch` sync occurs
# Uses `--host 0.0.0.0` to allow access from outside the container
# Note in production, you should use `fastapi run` instead
CMD ["uv", "run", "uwsgi", "-T", "--http", ":9001", "--uid", "www-data", "--gid", "www-data", "--enable-threads", "--wsgi-file", "./app.py", "--callable", "app"]
EXPOSE 9001
