# Makefile for Django + FastAPI Blog Project

.PHONY: help install test test-unit test-integration test-coverage lint format clean dev run

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "📦 Dependencies:"
	@echo "  install        Install all dependencies"
	@echo "  install-test   Install test dependencies only"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test           Run all tests (unit + integration)"
	@echo "  test-unit      Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-e2e       Run E2E tests (Playwright)"
	@echo "  test-coverage  Run tests with coverage report"
	@echo "  test-quick     Run quick tests (exclude slow)"
	@echo "  test-all       Run all tests including E2E"
	@echo ""
	@echo "🔍 Code Quality (Staged Approach):"
	@echo "  lint           Complete quality check (pre-commit)"
	@echo "  lint-core      Core code strict check (daily dev)"
	@echo "  lint-quick     Fast check (ruff + black)"
	@echo "  lint-full      Full integrated check (release)"
	@echo "  lint-e2e       E2E tests relaxed check"
	@echo "  format         Auto format code"
	@echo "  setup-hooks    Install pre-commit hooks"
	@echo "  audit          Security audit (pip-audit)"
	@echo ""
	@echo "🚀 Development:"
	@echo "  dev            Start development server"
	@echo "  migrate        Run Django migrations"
	@echo "  superuser      Create Django superuser"
	@echo "  shell          Django shell"
	@echo "  clean          Clean generated files"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  docker-dev     Start dev environment"
	@echo "  docker-full    Start full environment"
	@echo "  docker-down    Stop containers"
	@echo ""
	@echo "💡 Recommended workflow:"
	@echo "  Daily dev:     make lint-quick && make test-unit"
	@echo "  Before commit: make lint && make test"
	@echo "  Before PR:     make lint-full && make test-coverage"

# Install dependencies
install:
	uv sync --all-groups

# Install test dependencies only
install-test:
	uv sync --group test

# Run all tests (excluding E2E)
test: install-test
	uv run pytest tests/unit/ tests/integration/ -v

# Run unit tests only
test-unit: install-test
	uv run pytest tests/unit/ -m unit -v

# Run integration tests only
test-integration: install-test
	uv run pytest tests/integration/ -m integration -v

# Run tests with coverage (excluding E2E)
test-coverage: install-test
	uv run pytest tests/unit/ tests/integration/ --cov=fastapi_app --cov=blog --cov-report=term-missing --cov-report=html

# Run quick tests (excluding slow tests and E2E)
test-quick: install-test
	uv run pytest tests/unit/ tests/integration/ -m "not slow" -v

# E2E tests
test-e2e:
	uv sync --group e2e
	uv run playwright install
	uv run --group e2e pytest tests/e2e/ -v --tb=short --disable-warnings -o addopts="" --asyncio-mode=auto

# All tests including E2E
test-all: test test-e2e

# Code quality - staged approach
lint:
	uv run pre-commit run --all-files

lint-core:
	uv run flake8 fastapi_app/ blog/ main_asgi.py manage.py --max-line-length=88 --extend-ignore=E203,E501,E402
	uv run black --check fastapi_app/ blog/ main_asgi.py manage.py

lint-e2e:
	uv run black tests/e2e/ || echo "E2E formatting issues detected but not blocking"
	uv run flake8 tests/e2e/ --extend-ignore=E231,E272,E702,E202,E201,E221,E203,E501 || echo "E2E style issues detected but not blocking"

lint-full: lint lint-e2e
	@echo "✅ Complete quality check passed"

format: lint
	@echo "Formatting completed via pre-commit hooks"

# Quick lint check (for CI/rapid feedback)
lint-quick:
	uv run ruff check fastapi_app/ blog/ tests/unit/ tests/integration/ --fix || echo "Core lint issues detected"
	uv run black --check fastapi_app/ blog/ tests/unit/ tests/integration/

# Pre-commit setup
setup-hooks:
	uv run pre-commit install
	@echo "Pre-commit hooks installed successfully!"

check-hooks:
	uv run pre-commit run --all-files

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
	uv run pip-audit

# Docker commands
docker-build:
	docker build -f docker/Dockerfile -t my-wagtail-fastapi-blog .

docker-dev:
	docker-compose -f docker/docker-compose.dev.yml up --build -d

docker-full:
	docker-compose -f docker/docker-compose.yml up --build -d

docker-down:
	docker-compose -f docker/docker-compose.yml down

docker-clean:
	docker-compose -f docker/docker-compose.yml down -v
	docker system prune -f
