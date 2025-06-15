# Django + Wagtail + FastAPI Blog - Docker Development Environment

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY . .

# Install Python dependencies
RUN uv sync --all-groups

# Create directories for Django
RUN mkdir -p django_project/logs django_project/media django_project/staticfiles

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/posts/health || exit 1

# Default command
CMD ["uv", "run", "uvicorn", "main_asgi:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
