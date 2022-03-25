FROM python:3.10-slim-bullseye as base
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
RUN apt update && apt install -y libsqlite3-0

FROM base as builder
RUN apt update && apt install -y gcc libffi-dev g++ git
WORKDIR /app

ENV PYTHONHASHSEED=0 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.1.12


RUN pip install "poetry==$POETRY_VERSION" && poetry config virtualenvs.in-project true

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-interaction --no-ansi

from base as prod
COPY --from=builder /app /app
WORKDIR /app
COPY . .

CMD ["./entrypoint.sh"]
EXPOSE 9001
