FROM python:3.13-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml ./
RUN uv sync --no-dev --frozen || uv sync --no-dev
COPY config.py opencode_client.py server.py ./
ENV ACP_HOST=0.0.0.0
ENV ACP_PORT=8000
EXPOSE 8000
CMD ["uv", "run", "server.py"]
