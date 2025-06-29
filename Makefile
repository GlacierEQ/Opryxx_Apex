# ===================================================================
# OPRYXX AI Workbench - Comprehensive Build and Automation System
# ===================================================================

# Detect OS
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    OS = linux
    DOCKER_COMPOSE = docker-compose -f docker-compose.yml -f docker-compose.linux.yml
else ifeq ($(OS),Windows_NT)
    OS = windows
    DOCKER_COMPOSE = docker-compose -f docker-compose.yml -f docker-compose.windows.yml
else ifeq ($(UNAME_S),Darwin)
    OS = darwin
    DOCKER_COMPOSE = docker-compose -f docker-compose.yml -f docker-compose.macos.yml
else
    $(error OS not supported by this Makefile)
endif

# Python and environment variables
PYTHON = python3
PIP = pip3
PYTEST = pytest
COVERAGE = coverage
BLACK = black
ISORT = isort
FLAKE8 = flake8
MYPY = mypy
BANDIT = bandit
SAFETY = safety
PYLINT = pylint
DOCKER = docker
DOCKER_COMPOSE = docker-compose
NPM = npm
NODE = node

# Project variables
PROJECT_NAME = opryxx
PACKAGE_NAME = $(shell $(PYTHON) setup.py --name | tr '[:upper:]' '[:lower:]')
VERSION = $(shell $(PYTHON) -c "import $(PACKAGE_NAME); print($(PACKAGE_NAME).__version__)")
PYTHON_VERSION = $(shell $(PYTHON) -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

# Directories
SRC_DIR = src
TEST_DIR = tests
DOCS_DIR = docs
DIST_DIR = dist
BUILD_DIR = build
COVERAGE_DIR = htmlcov

# Files
REQUIREMENTS = requirements.txt
REQUIREMENTS_DEV = requirements-dev.txt
SETUP_FILE = setup.py
DOCKER_FILE = Dockerfile
DOCKER_COMPOSE_FILE = docker-compose.yml
DOCKER_COMPOSE_OVERRIDE = docker-compose.override.yml
DOCKER_COMPOSE_TEST = docker-compose.test.yml
DOCKER_COMPOSE_PROD = docker-compose.prod.yml
DOCKER_COMPOSE_DEV = docker-compose.dev.yml

# Docker
DOCKER_IMAGE = $(PACKAGE_NAME):$(VERSION)
DOCKER_IMAGE_LATEST = $(PACKAGE_NAME):latest
DOCKER_REGISTRY = ghcr.io/your-username/$(PACKAGE_NAME)
DOCKER_REGISTRY_IMAGE = $(DOCKER_REGISTRY):$(VERSION)
DOCKER_REGISTRY_LATEST = $(DOCKER_REGISTRY):latest

# Phony targets
.PHONY: help \
        # Build and installation
        build build-wheel build-sdist build-docker \
        install install-dev install-test install-docs install-all \
        uninstall clean clean-build clean-pyc clean-test clean-docker clean-all \
        # Testing
        test test-unit test-integration test-e2e test-coverage test-html test-xml \
        test-all test-report test-clean \
        # Linting and formatting
        lint lint-flake8 lint-pylint lint-mypy lint-bandit lint-safety \
        format format-black format-isort format-docs \
        check-format check-format-black check-format-isort \
        check-all check-security check-dependencies check-licenses \
        # Documentation
        docs docs-html docs-pdf docs-serve docs-clean \
        # Docker
        docker-build docker-push docker-pull docker-tag docker-run docker-exec \
        docker-logs docker-stop docker-rm docker-rmi docker-clean \
        # Docker Compose
        compose-up compose-down compose-restart compose-logs compose-ps \
        compose-build compose-push compose-pull compose-clean \
        # Development
        dev-install dev-setup dev-reset dev-shell dev-test dev-lint dev-format \
        # Deployment
        deploy-staging deploy-production deploy-rollback deploy-status \
        # Release
        release-major release-minor release-patch release-version \
        bump-version bump-major bump-minor bump-patch \
        # Dependencies
        deps-update deps-outdated deps-audit deps-licenses \
        # System
        system-info system-check system-setup system-update

# Help
help: ## Display this help message
	@echo "\n\033[1m$(PROJECT_NAME) - Comprehensive Build and Automation System\033[0m\n"
	@echo "\033[1mBuild and Installation:\033[0m"
	@echo "  build               Build package"
	@echo "  build-wheel         Build wheel package"
	@echo "  build-sdist         Build source distribution"
	@echo "  build-docker        Build Docker image"
	@echo "  install             Install production dependencies"
	@echo "  install-dev         Install development dependencies"
	@echo "  install-test        Install test dependencies"
	@echo "  install-docs        Install documentation dependencies"
	@echo "  install-all         Install all dependencies"
	@echo "  uninstall           Uninstall package"

	@echo "\n\033[1mTesting:\033[0m"
	@echo "  test                Run all tests"
	@echo "  test-unit           Run unit tests"
	@echo "  test-integration    Run integration tests"
	@echo "  test-e2e            Run end-to-end tests"
	@echo "  test-coverage       Run tests with coverage report"
	@echo "  test-html           Generate HTML coverage report"
	@echo "  test-xml            Generate XML coverage report"
	@echo "  test-all            Run all tests with coverage and reports"
	@echo "  test-report         Generate test reports"

	@echo "\n\033[1mLinting and Formatting:\033[0m"
	@echo "  lint                Run all linters"
	@echo "  lint-flake8         Run flake8 linter"
	@echo "  lint-pylint         Run pylint"
	@echo "  lint-mypy           Run mypy type checking"
	@echo "  lint-bandit         Run bandit security checks"
	@echo "  lint-safety         Run safety dependency checks"
	@echo "  format              Format code"
	@echo "  format-black        Format code with black"
	@echo "  format-isort        Sort imports with isort"
	@echo "  format-docs         Format documentation"
	@echo "  check-format        Check code formatting"
	@echo "  check-all           Run all checks"

	@echo "\n\033[1mDocumentation:\033[0m"
	@echo "  docs                Generate documentation"
	@echo "  docs-html           Generate HTML documentation"
	@echo "  docs-pdf            Generate PDF documentation"
	@echo "  docs-serve          Serve documentation locally"
	@echo "  docs-clean          Clean documentation"

	@echo "\n\033[1mDocker:\033[0m"
	@echo "  docker-build        Build Docker image"
	@echo "  docker-push         Push Docker image to registry"
	@echo "  docker-pull         Pull Docker image from registry"
	@echo "  docker-tag          Tag Docker image"
	@echo "  docker-run          Run Docker container"
	@echo "  docker-exec         Execute command in running container"
	@echo "  docker-logs         Show container logs"
	@echo "  docker-stop         Stop container"
	@echo "  docker-rm           Remove container"
	@echo "  docker-rmi          Remove image"
	@echo "  docker-clean        Clean Docker resources"

	@echo "\n\033[1mDocker Compose:\033[0m"
	@echo "  compose-up          Start services"
	@echo "  compose-down        Stop services"
	@echo "  compose-restart     Restart services"
	@echo "  compose-logs        Show service logs"
	@echo "  compose-ps          List services"
	@echo "  compose-build       Build service images"
	@echo "  compose-push        Push service images"
	@echo "  compose-pull        Pull service images"
	@echo "  compose-clean       Clean compose resources"

	@echo "\n\033[1mDevelopment:\033[0m"
	@echo "  dev-install         Install development environment"
	@echo "  dev-setup           Setup development environment"
	@echo "  dev-reset           Reset development environment"
	@echo "  dev-shell           Start development shell"
	@echo "  dev-test            Run development tests"
	@echo "  dev-lint            Run development linters"
	@echo "  dev-format          Format development code"

	@echo "\n\033[1mDeployment:\033[0m"
	@echo "  deploy-staging      Deploy to staging"
	@echo "  deploy-production   Deploy to production"
	@echo "  deploy-rollback     Rollback deployment"
	@echo "  deploy-status       Check deployment status"

	@echo "\n\033[1mRelease Management:\033[0m"
	@echo "  release-major       Create major release"
	@echo "  release-minor       Create minor release"
	@echo "  release-patch       Create patch release"
	@echo "  release-version     Create specific version release"
	@echo "  bump-version        Bump version"
	@echo "  bump-major          Bump major version"
	@echo "  bump-minor          Bump minor version"
	@echo "  bump-patch          Bump patch version"

	@echo "\n\033[1mDependency Management:\033[0m"
	@echo "  deps-update         Update dependencies"
	@echo "  deps-outdated       Check for outdated dependencies"
	@echo "  deps-audit          Audit dependencies for vulnerabilities"
	@echo "  deps-licenses       Check dependency licenses"

	@echo "\n\033[1mSystem:\033[0m"
	@echo "  system-info         Show system information"
	@echo "  system-check        Run system checks"
	@echo "  system-setup        Setup system"
	@echo "  system-update       Update system"

	@echo "\n\033[1mCleaning:\033[0m"
	@echo "  clean               Remove Python file artifacts"
	@echo "  clean-build         Remove build artifacts"
	@echo "  clean-pyc           Remove Python file artifacts"
	@echo "  clean-test          Remove test artifacts"
	@echo "  clean-docker        Remove Docker resources"
	@echo "  clean-all           Remove all build, test, coverage and Python artifacts"

	@echo "\nUse 'make <target>' where <target> is one of the above.\n"
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

# Build and Installation
build: clean-build build-wheel build-sdist ## Build package

build-wheel: ## Build wheel package
	@echo "Building wheel package..."
	$(PYTHON) setup.py bdist_wheel

build-sdist: ## Build source distribution
	@echo "Building source distribution..."
	$(PYTHON) setup.py sdist

build-docker: ## Build Docker image
	@echo "Building Docker image..."
	$(DOCKER) build -t $(DOCKER_IMAGE) .

install: ## Install production dependencies
	@echo "Installing production dependencies..."
	$(PIP) install -r $(REQUIREMENTS)

install-dev: ## Install development dependencies
	@echo "Installing development dependencies..."
	$(PIP) install -r $(REQUIREMENTS_DEV)

install-test: ## Install test dependencies
	@echo "Installing test dependencies..."
	$(PIP) install pytest pytest-cov pytest-xdist

install-docs: ## Install documentation dependencies
	@echo "Installing documentation dependencies..."
	$(PIP) install -r docs/requirements.txt

install-all: install install-dev install-test install-docs ## Install all dependencies

uninstall: ## Uninstall package
	@echo "Uninstalling package..."
	$(PIP) uninstall -y $(PACKAGE_NAME)

# Cleaning
clean: clean-build clean-pyc clean-test clean-docker ## Remove Python file artifacts

clean-build: ## Remove build artifacts
	@echo "Removing build artifacts..."
	rm -fr $(BUILD_DIR)/
	rm -fr $(DIST_DIR)/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## Remove Python file artifacts
	@echo "Removing Python file artifacts..."
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## Remove test artifacts
	@echo "Removing test artifacts..."
	rm -f .coverage
	rm -fr $(COVERAGE_DIR)/
	rm -fr .pytest_cache/
	rm -fr .mypy_cache/

clean-docker: ## Remove Docker resources
	@echo "Removing Docker resources..."
	$(DOCKER) system prune -f
	$(DOCKER) volume prune -f

clean-all: clean clean-docker ## Remove all build, test, coverage and Python artifacts

# Testing
test: test-unit test-integration test-e2e ## Run all tests

TEST_ARGS = -v --cov=$(PACKAGE_NAME) --cov-report=term-missing
PYTEST_ARGS = -n auto --dist=loadfile $(TEST_ARGS)

test-unit: ## Run unit tests
	@echo "Running unit tests..."
	$(PYTEST) $(TEST_DIR)/unit $(PYTEST_ARGS) --cov-fail-under=80

test-integration: ## Run integration tests
	@echo "Running integration tests..."
	$(PYTEST) $(TEST_DIR)/integration $(PYTEST_ARGS)

test-e2e: ## Run end-to-end tests
	@echo "Running end-to-end tests..."
	$(PYTEST) $(TEST_DIR)/e2e $(PYTEST_ARGS)

test-coverage: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	$(PYTEST) --cov=$(PACKAGE_NAME) --cov-report=term-missing --cov-report=html

test-html: test-coverage ## Generate HTML coverage report
	@echo "Generating HTML coverage report..."
	$(PYTEST) --cov=$(PACKAGE_NAME) --cov-report=html
	@echo "Coverage report available at $(COVERAGE_DIR)/index.html"

test-xml: ## Generate XML coverage report
	@echo "Generating XML coverage report..."
	$(PYTEST) --cov=$(PACKAGE_NAME) --cov-report=xml:coverage.xml

test-all: clean test-html test-xml ## Run all tests with coverage and reports

# Linting and Formatting
lint: lint-flake8 lint-pylint lint-mypy lint-bandit lint-safety ## Run all linters

lint-flake8: ## Run flake8 linter
	@echo "Running flake8..."
	$(FLAKE8) $(SRC_DIR) $(TEST_DIR) --max-line-length=88 --exclude=.git,__pycache__,.pytest_cache

lint-pylint: ## Run pylint
	@echo "Running pylint..."
	$(PYLINT) $(SRC_DIR) $(TEST_DIR) --rcfile=.pylintrc

lint-mypy: ## Run mypy type checking
	@echo "Running mypy..."
	$(MYPY) $(SRC_DIR) $(TEST_DIR) --config-file=mypy.ini

lint-bandit: ## Run bandit security checks
	@echo "Running bandit..."
	$(BANDIT) -r $(SRC_DIR) -c bandit.yml

lint-safety: ## Run safety dependency checks
	@echo "Running safety..."
	$(SAFETY) check --full-report

format: format-black format-isort format-docs ## Format code

format-black: ## Format code with black
	@echo "Formatting code with black..."
	$(BLACK) $(SRC_DIR) $(TEST_DIR) setup.py

format-isort: ## Sort imports with isort
	@echo "Sorting imports with isort..."
	$(ISORT) $(SRC_DIR) $(TEST_DIR) setup.py

format-docs: ## Format documentation
	@echo "Formatting documentation..."
	@# Add documentation formatting commands here

check-format: check-format-black check-format-isort ## Check code formatting

check-format-black: ## Check black formatting
	@echo "Checking black formatting..."
	$(BLACK) --check $(SRC_DIR) $(TEST_DIR) setup.py

check-format-isort: ## Check isort formatting
	@echo "Checking isort formatting..."
	$(ISORT) --check-only $(SRC_DIR) $(TEST_DIR) setup.py

check-all: lint test check-format ## Run all checks

# Docker
docker-build: ## Build Docker image
	@echo "Building Docker image..."
	$(DOCKER) build -t $(DOCKER_IMAGE) .

docker-push: ## Push Docker image to registry
	@echo "Pushing Docker image to registry..."
	$(DOCKER) tag $(DOCKER_IMAGE) $(DOCKER_REGISTRY_IMAGE)
	$(DOCKER) push $(DOCKER_REGISTRY_IMAGE)

docker-pull: ## Pull Docker image from registry
	@echo "Pulling Docker image from registry..."
	$(DOCKER) pull $(DOCKER_REGISTRY_IMAGE)

docker-tag: ## Tag Docker image
	@echo "Tagging Docker image..."
	$(DOCKER) tag $(DOCKER_IMAGE) $(DOCKER_IMAGE_LATEST)
	$(DOCKER) tag $(DOCKER_IMAGE) $(DOCKER_REGISTRY_IMAGE)
	$(DOCKER) tag $(DOCKER_IMAGE) $(DOCKER_REGISTRY_LATEST)

docker-run: ## Run Docker container
	@echo "Running Docker container..."
	$(DOCKER) run --rm -it $(DOCKER_IMAGE)

docker-exec: ## Execute command in running container
	@echo "Executing command in container..."
	$(DOCKER) exec -it $(shell docker ps -q -f name=$(PACKAGE_NAME)) $(cmd)

docker-logs: ## Show container logs
	@echo "Showing container logs..."
	$(DOCKER) logs -f $(shell docker ps -q -f name=$(PACKAGE_NAME))

docker-stop: ## Stop container
	@echo "Stopping container..."
	$(DOCKER) stop $(shell docker ps -q -f name=$(PACKAGE_NAME))

docker-rm: ## Remove container
	@echo "Removing container..."
	$(DOCKER) rm -f $(shell docker ps -a -q -f name=$(PACKAGE_NAME))

docker-rmi: ## Remove image
	@echo "Removing image..."
	$(DOCKER) rmi -f $(DOCKER_IMAGE)

docker-clean: ## Clean Docker resources
	@echo "Cleaning Docker resources..."
	$(DOCKER) system prune -f
	$(DOCKER) volume prune -f

# Docker Compose
compose-up: ## Start services
	@echo "Starting services..."
	$(DOCKER_COMPOSE) up -d

compose-down: ## Stop services
	@echo "Stopping services..."
	$(DOCKER_COMPOSE) down

compose-restart: compose-down compose-up ## Restart services

compose-logs: ## Show service logs
	@echo "Showing service logs..."
	$(DOCKER_COMPOSE) logs -f

compose-ps: ## List services
	@echo "Listing services..."
	$(DOCKER_COMPOSE) ps

compose-build: ## Build service images
	@echo "Building service images..."
	$(DOCKER_COMPOSE) build

compose-push: ## Push service images
	@echo "Pushing service images..."
	$(DOCKER_COMPOSE) push

compose-pull: ## Pull service images
	@echo "Pulling service images..."
	$(DOCKER_COMPOSE) pull

compose-clean: ## Clean compose resources
	@echo "Cleaning compose resources..."
	$(DOCKER_COMPOSE) down -v --remove-orphans
	$(DOCKER_COMPOSE) rm -f -v

# Development
dev-install: install-dev install-test install-docs ## Install development environment
	@echo "Development environment installed"

dev-setup: ## Setup development environment
	@echo "Setting up development environment..."
	pre-commit install
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .[dev]

dev-reset: clean-all ## Reset development environment
	@echo "Resetting development environment..."
	git clean -fdx

dev-shell: ## Start development shell
	@echo "Starting development shell..."
	$(PYTHON) -m ipython --no-banner

dev-test: test ## Run development tests
	@echo "Running development tests..."

# Deployment
deploy-staging: ## Deploy to staging
	@echo "Deploying to staging..."
	$(DOCKER_COMPOSE) -f docker-compose.staging.yml up -d

deploy-production: ## Deploy to production
	@echo "Deploying to production..."
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml up -d

deploy-rollback: ## Rollback deployment
	@echo "Rolling back deployment..."
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml pull
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml up -d --force-recreate

deploy-status: ## Check deployment status
	@echo "Checking deployment status..."
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml ps

# Release Management
release-major: ## Create major release
	@echo "Creating major release..."
	$(eval NEW_VERSION := $(shell bump2version --dry-run --list major | grep new_version | sed 's/^.*=//'))
	@echo "New version: $(NEW_VERSION)"
	git flow release start $(NEW_VERSION)
	bump2version major
	git flow release finish -m "Release $(NEW_VERSION)" $(NEW_VERSION)
	git push origin develop main
	git push --tags

release-minor: ## Create minor release
	@echo "Creating minor release..."
	$(eval NEW_VERSION := $(shell bump2version --dry-run --list minor | grep new_version | sed 's/^.*=//'))
	@echo "New version: $(NEW_VERSION)"
	git flow release start $(NEW_VERSION)
	bump2version minor
	git flow release finish -m "Release $(NEW_VERSION)" $(NEW_VERSION)
	git push origin develop main
	git push --tags

release-patch: ## Create patch release
	@echo "Creating patch release..."
	$(eval NEW_VERSION := $(shell bump2version --dry-run --list patch | grep new_version | sed 's/^.*=//'))
	@echo "New version: $(NEW_VERSION)"
	git flow release start $(NEW_VERSION)
	bump2version patch
	git flow release finish -m "Release $(NEW_VERSION)" $(NEW_VERSION)
	git push origin develop main
	git push --tags

release-version: ## Create specific version release
	@echo "Creating release for version $(version)..."
	git flow release start $(version)
	echo "$(version)" > VERSION
	git add VERSION
	git commit -m "Bump version to $(version)"
	git flow release finish -m "Release $(version)" $(version)
	git push origin develop main
	git push --tags

bump-version: ## Bump version (major.minor.patch)
	@echo "Bumping version..."
	bump2version $(bump)

bump-major: ## Bump major version
	@echo "Bumping major version..."
	bump2version major

bump-minor: ## Bump minor version
	@echo "Bumping minor version..."
	bump2version minor

bump-patch: ## Bump patch version
	@echo "Bumping patch version..."
	bump2version patch

# Dependency Management
deps-update: ## Update dependencies
	@echo "Updating dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQUIREMENTS_DEV)
	$(PIP) freeze > $(REQUIREMENTS)

# System
system-info: ## Show system information
	@echo "System information:"
	@echo "------------------"
	@echo "OS: $(shell uname -a)"
	@echo "Python: $(shell python --version)"
	@echo "Pip: $(shell pip --version)"
	@echo "Docker: $(shell docker --version)"
	@echo "Docker Compose: $(shell docker-compose --version)"

system-check: ## Run system checks
	@echo "Running system checks..."
	$(PYTHON) manage.py check --deploy

system-setup: ## Setup system
	@echo "Setting up system..."
	# Add system setup commands here

system-update: ## Update system
	@echo "Updating system..."
	# Add system update commands here

# Docker Compose test environment
DOCKER_COMPOSE_TEST = docker-compose -f docker-compose.yml -f docker-compose.test.yml

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
