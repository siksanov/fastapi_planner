from python:3.13-alpine

copy --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

add . /app

workdir /app/

run uv sync --locked

cmd ["uv", "run", "app/main.py"]