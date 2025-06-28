.PHONY: help build test lint format check-format security clean docker-build docker-push docker-pull \
        docker-up docker-down docker-logs docker-restart docker-test docker-test-coverage \
        docker-test-lint docker-test-security docker-test-load docker-test-all \
        deploy-staging deploy-production logs-staging logs-production \
        monitor monitor-logs monitor-metrics monitor-tracing \
        docs docs-serve \
        db-migrate db-upgrade db-downgrade db-reset \
        shell shell-db shell-redis \
        install install-dev install-test install-prod

# Help
help:
	@echo "\n\033[1mOPRYXX AI Workbench - Development and Deployment\033[0m\n"
	@echo "\033[1mDevelopment:\033[0m"
	@echo "  install             Install production dependencies"
	@echo "  install-dev         Install development dependencies"
	@echo "  install-test        Install test dependencies"
	@echo "  install-prod        Install production dependencies"
	@echo "  test                Run tests with pytest"
	@echo "  test-coverage       Run tests with coverage report"
	@echo "  lint                Run code style checks"
	@echo "  format              Format code with black and isort"
	@echo "  check-format        Check code formatting"
	@echo "  security            Run security checks"
	@echo "  docs                Generate documentation"
	@echo "  docs-serve          Serve documentation locally"
	@echo "\n\033[1mDocker Compose:\033[0m"
	@echo "  docker-up           Start all services"
	@echo "  docker-down         Stop all services"
	@echo "  docker-restart      Restart all services"
	@echo "  docker-logs         View logs for all services"
	@echo "  docker-build        Build all Docker images"
	@echo "  docker-push         Push Docker images to registry"
	@echo "  docker-pull         Pull Docker images from registry"
	@echo "\n\033[1mTesting (Docker):\033[0m"
	@echo "  docker-test         Run tests in Docker"
	@echo "  docker-test-coverage Run tests with coverage in Docker"
	@echo "  docker-test-lint    Run linting in Docker"
	@echo "  docker-test-security Run security checks in Docker"
	@echo "  docker-test-load    Run load tests in Docker"
	@echo "  docker-test-all     Run all tests in Docker"
	@echo "\n\033[1mDeployment:\033[0m"
	@echo "  deploy-staging      Deploy to staging environment"
	@echo "  deploy-production   Deploy to production environment"
	@echo "  logs-staging        View logs for staging"
	@echo "  logs-production     View logs for production"
	@echo "\n\033[1mMonitoring:\033[0m"
	@echo "  monitor             Open monitoring dashboard"
	@echo "  monitor-logs        Open logs dashboard"
	@echo "  monitor-metrics     Open metrics dashboard"
	@echo "  monitor-tracing     Open distributed tracing"
	@echo "\n\033[1mDatabase:\033[0m"
	@echo "  db-migrate          Create a new migration"
	@echo "  db-upgrade          Upgrade database to latest migration"
	@echo "  db-downgrade        Downgrade database by one migration"
	@echo "  db-reset            Reset database (DANGER: drops all data)"
	@echo "\n\033[1mShell Access:\033[0m"
	@echo "  shell               Open shell in app container"
	@echo "  shell-db            Open PostgreSQL shell"
	@echo "  shell-redis         Open Redis CLI"

# Environment variables
ENV_FILE ?= .env
DOCKER_COMPOSE = docker-compose -f docker-compose.yml
DOCKER_COMPOSE_DEV = $(DOCKER_COMPOSE) -f docker-compose.override.yml
DOCKER_COMPOSE_TEST = docker-compose -f docker-compose.test.yml
DOCKER_COMPOSE_PROD = docker-compose -f docker-compose.yml -f docker-compose.prod.yml

# Include environment file if it exists
ifneq (,$(wildcard $(ENV_FILE)))
include $(ENV_FILE)
export $(shell sed 's/=.*//' $(ENV_FILE))
endif

# Development
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

install-test:
	pip install -e ".[test]"

install-prod:
	pip install -e ".[prod]"

test:
	pytest -v --cov=ai_workbench --cov-report=term-missing tests/

test-coverage:
	pytest --cov=ai_workbench --cov-report=html --cov-report=xml tests/
	coverage report -m

lint:
	black --check .
	isort --check-only .
	flake8
	mypy .

format:
	black .
	isort .


check-format:
	black --check .
	isort --check-only .


security:
	safety check --full-report
	bandit -r . -x ./tests,./venv

docs:
	mkdocs build --clean

docs-serve:
	mkdocs serve

# Docker Compose
docker-up:
	$(DOCKER_COMPOSE_DEV) up -d

docker-down:
	$(DOCKER_COMPOSE_DEV) down

docker-restart:
	$(DOCKER_COMPOSE_DEV) restart

docker-logs:
	$(DOCKER_COMPOSE_DEV) logs -f

docker-build:
	$(DOCKER_COMPOSE_DEV) build

docker-push:
	echo "Pushing images to registry..."
	@# Add your registry push commands here

# Testing (Docker)
docker-test:
	$(DOCKER_COMPOSE_TEST) run --rm test

docker-test-coverage:
	$(DOCKER_COMPOSE_TEST) run --rm test-coverage

docker-test-lint:
	$(DOCKER_COMPOSE_TEST) run --rm test-lint

docker-test-security:
	$(DOCKER_COMPOSE_TEST) run --rm test-security

docker-test-load:
	$(DOCKER_COMPOSE_TEST) up -d app
	$(DOCKER_COMPOSE_TEST) run --rm test-load

# Run all tests in Docker
docker-test-all:
	$(DOCKER_COMPOSE_TEST) run --rm test-lint
	$(DOCKER_COMPOSE_TEST) run --rm test-security
	$(DOCKER_COMPOSE_TEST) run --rm test
	$(DOCKER_COMPOSE_TEST) run --rm test-coverage

# Deployment
deploy-staging:
	echo "Deploying to staging..."
	@# Add your staging deployment commands here

deploy-production:
	echo "Deploying to production..."
	@# Add your production deployment commands here

logs-staging:
	$(DOCKER_COMPOSE) -f docker-compose.staging.yml logs -f

logs-production:
	$(DOCKER_COMPOSE_PROD) logs -f

# Monitoring
monitor:
	open http://localhost:3000

monitor-logs:
	open http://localhost:3000/explore?orgId=1&left=%5B%22now-1h%22,%22now%22,%22Loki%22,%7B%22expr%22:%22%7Bcontainer_name%3D%5C%22opryxx-app%5C%22%7D%22%7D%5D

monitor-metrics:
	open http://localhost:3000/d/opryxx/opryxx-metrics

monitor-tracing:
	open http://localhost:16686

# Database
db-migrate:
	alembic revision --autogenerate -m "$(filter-out $@,$(MAKECMDGOALS))"

db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

db-reset:
	@echo "WARNING: This will drop all data in the database!"
	@read -p "Are you sure you want to continue? [y/N] " ans && [ $${ans:-N} = y ]
	$(DOCKER_COMPOSE_DEV) exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	alembic upgrade head

# Shell Access
shell:
	$(DOCKER_COMPOSE_DEV) exec app /bin/bash

shell-db:
	$(DOCKER_COMPOSE_DEV) exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

shell-redis:
	$(DOCKER_COMPOSE_DEV) exec redis redis-cli -a $(REDIS_PASSWORD)

# Helper target to handle arguments with spaces
%:
	@:
