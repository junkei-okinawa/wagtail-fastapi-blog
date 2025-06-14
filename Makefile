# Makefile for Django + FastAPI Blog Project

.PHONY: help install test test-unit test-integration test-coverage lint format clean dev run

# Default target
help:
	@echo "Available commands:"
	@echo "  install        Install dependencies"
	@echo "  test           Run all tests"
	@echo "  test-unit      Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-coverage  Run tests with coverage report"
	@echo "  lint           Run linting checks"
	@echo "  format         Format code"
	@echo "  clean          Clean up generated files"
	@echo "  dev            Start development server"
	@echo "  migrate        Run Django migrations"

# Install dependencies
install:
	uv sync --all-groups

# Install test dependencies only
install-test:
	uv sync --group test

# Run all tests
test: install-test
	uv run pytest

# Run unit tests only
test-unit: install-test
	uv run pytest tests/unit/ -m unit -v

# Run integration tests only
test-integration: install-test
	uv run pytest tests/integration/ -m integration -v

# Run tests with coverage
test-coverage: install-test
	uv run pytest --cov=fastapi_app --cov=blog --cov-report=term-missing --cov-report=html

# Run quick tests (excluding slow tests)
test-quick: install-test
	uv run pytest -m "not slow" -v

# Lint code
lint:
	uv run ruff check .
	uv run flake8 fastapi_app blog tests

# Format code
format:
	uv run ruff format .
	uv run isort fastapi_app blog tests

# Clean up generated files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/

# Start development server
dev:
	uv run uvicorn main_asgi:app --reload --host 127.0.0.1 --port 8000

# Run Django migrations
migrate:
	uv run python manage.py migrate

# Create superuser
superuser:
	uv run python manage.py createsuperuser

# Collect static files
collectstatic:
	uv run python manage.py collectstatic --noinput

# Run Django shell
shell:
	uv run python manage.py shell

# Database shell
dbshell:
	uv run python manage.py dbshell

# Check Django deployment readiness
check:
	uv run python manage.py check --deploy

# Create test data
create-test-data:
	uv run python manage.py shell -c "
	from wagtail.models import Page, Site; 
	from blog.models import BlogPage; 
	from wagtail.rich_text import RichText;
	root = Page.objects.get(title='Root');
	for i in range(5):
		blog = BlogPage(title=f'Test Post {i+1}', intro=f'Test intro {i+1}', body=RichText(f'<p>Test content {i+1}</p>'), slug=f'test-post-{i+1}');
		root.add_child(instance=blog);
		blog.save()
	"

# Run tests in CI environment
test-ci: install-test
	uv run pytest --cov=fastapi_app --cov=blog --cov-report=xml --cov-report=term --junitxml=junit.xml

# Security audit
audit:
	uv run safety check
