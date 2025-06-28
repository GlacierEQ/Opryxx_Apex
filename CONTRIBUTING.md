# Contributing to OPRYXX AI Workbench

Thank you for your interest in contributing to OPRYXX AI Workbench! We appreciate your time and effort in helping us improve this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)
- [Documentation](#documentation)
- [Testing](#testing)
- [Code Review](#code-review)
- [Security](#security)
- [License](#license)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Configure** the upstream remote
4. **Create a branch** for your changes
5. **Commit** your changes
6. **Push** your changes to your fork
7. **Open a Pull Request**

## Development Environment Setup

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- PostgreSQL 14+
- Redis 7+

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/opryxx-ai-workbench.git
   cd opryxx-ai-workbench
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\\venv\\Scripts\\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Start the development services:
   ```bash
   docker-compose up -d postgres redis
   ```

6. Run database migrations:
   ```bash
   alembic upgrade head
   ```

7. Start the development server:
   ```bash
   uvicorn ai_workbench.api.app:create_app --reload
   ```

## Project Structure

```
opryxx-ai-workbench/
├── ai_workbench/           # Main application package
│   ├── api/                # API endpoints and routes
│   ├── core/               # Core business logic
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic models
│   ├── services/           # Business logic services
│   ├── utils/              # Utility functions
│   └── config.py           # Application configuration
├── tests/                  # Test suite
├── alembic/                # Database migrations
├── docker/                 # Docker configuration
├── docs/                   # Documentation
├── .env                    # Environment variables
├── .gitignore             
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Production Dockerfile
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── README.md              # Project documentation
```

## Coding Standards

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for all function signatures
- Keep functions small and focused
- Write docstrings for all public functions, classes, and methods
- Use absolute imports
- Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

### Frontend

- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use functional components with hooks
- Follow the [React Hooks API Reference](https://reactjs.org/docs/hooks-reference.html)
- Use TypeScript for type safety
- Follow the [TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)

## Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for our commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies
- **ci**: Changes to our CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

### Examples

```
feat(auth): add login with Google

Add OAuth2 authentication using Google as an identity provider.
Closes #123
```

```
fix(api): handle null values in user profile

- Add null checks for optional fields
- Update tests to cover edge cases

Fixes #456
```

## Pull Request Process

1. Fork the repository and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Update the CHANGELOG.md with your changes
7. Open a pull request

## Reporting Bugs

Please use GitHub issues to report bugs. Include the following information:

1. A clear and descriptive title
2. Steps to reproduce the issue
3. Expected behavior
4. Actual behavior
5. Screenshots if applicable
6. Environment details (OS, browser, version, etc.)

## Feature Requests

We welcome feature requests! Please open an issue to discuss your idea before implementing it.

## Documentation

Good documentation is crucial for the success of any project. When contributing:

- Update the README.md with any changes to the setup process
- Document new features and configuration options
- Add examples where appropriate
- Keep the API documentation up to date

## Testing

Write tests for all new functionality. Follow these guidelines:

- Use pytest for all tests
- Follow the Arrange-Act-Assert pattern
- Use descriptive test names
- Mock external dependencies
- Aim for high test coverage

Run the test suite with:

```bash
pytest
```

## Code Review

All code must be reviewed before merging. When reviewing code:

- Be respectful and constructive
- Focus on the code, not the person
- Suggest improvements clearly
- Check for security vulnerabilities
- Ensure tests are in place
- Verify documentation is updated

## Security

If you discover a security vulnerability, please report it responsibly by emailing security@example.com. Do not create a public GitHub issue.

## License

By contributing, you agree that your contributions will be licensed under the project's [LICENSE](LICENSE) file.
