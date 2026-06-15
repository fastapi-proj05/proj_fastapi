FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

# AI 의존성 포함 설치
RUN uv sync --frozen --no-dev --extra ai

COPY worker/ ./worker/
COPY app/core/ ./app/core/

CMD ["uv", "run", "python", "-m", "worker.main"]