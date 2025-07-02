# OPRYXX Recovery System CI/CD Documentation

## Table of Contents
- [Overview](#overview)
- [Workflow Details](#workflow-details)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Test Execution](#test-execution)
- [Troubleshooting](#troubleshooting)
- [Customization](#customization)
- [Security Considerations](#security-considerations)

## Overview

The CI/CD pipeline for the OPRYXX Recovery System automates testing across multiple Python versions and Windows environments. It ensures code quality and reliability through comprehensive test coverage and automated reporting.

## Workflow Details

### Trigger Events
- **Push Events**: Triggered when changes are pushed to recovery-related files
- **Pull Requests**: Runs on PRs targeting the main branch
- **Manual Trigger**: Can be manually triggered from GitHub Actions

### Jobs

1. **Test**
   - Runs on: `windows-latest`
   - Python versions: 3.8, 3.9, 3.10, 3.11
   - Steps:
     - Checkout code
     - Set up Python
     - Install dependencies
     - Run unit tests with coverage
     - Run integration tests
     - Upload coverage to Codecov

2. **Windows Recovery Test**
   - Runs on: `windows-latest`
   - Tests Windows-specific recovery functionality
   - Includes mocked system calls

## Prerequisites

### GitHub Repository Settings
1. Required secrets:
   - `CODECOV_TOKEN`: For code coverage reporting
   - `TEST_PYPI_API_KEY`: For test package deployment (if enabled)

### Local Development
- Python 3.8+
- Windows 10/11 (for full test compatibility)
- Git

## Setup Instructions

### 1. Fork and Clone
```bash
git clone https://github.com/your-org/OPRYXX_LOGS.git
cd OPRYXX_LOGS
```

### 2. Set Up Python Environment
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
```

### 3. Configure Pre-commit Hooks (Optional)
```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install
```

## Test Execution

### Local Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_recovery_system.py -v

# Run with coverage
pytest --cov=recovery --cov-report=html
```

### CI/CD Pipeline
1. Push changes to a branch
2. Open a pull request
3. GitHub Actions will automatically run tests
4. View results in the "Actions" tab

## Workflow Customization

### Environment Variables
Edit `.github/workflows/test_recovery.yml` to modify:
- Python versions
- Test command options
- Code quality checks

### Adding New Tests
1. Create test files in `tests/`
2. Name test files with `test_` prefix
3. Use pytest fixtures for common setup/teardown

## Troubleshooting

### Common Issues

#### Tests Failing in CI
1. Check the workflow logs
2. Look for error messages
3. Reproduce locally with the same Python version

#### Coverage Report Missing
1. Verify `CODECOV_TOKEN` is set
2. Check for test failures
3. Ensure tests are properly annotated

#### Windows-Specific Failures
1. Test on a Windows machine
2. Check file path handling
3. Verify Windows API calls are mocked

### Debugging
```yaml
# Add debug logging to workflow
- name: Debug Info
  run: |
    python --version
    pip list
    systeminfo
```

## Security Considerations

### Secrets Management
- Never commit sensitive data
- Use GitHub Secrets for credentials
- Restrict repository access

### Dependency Security
- Regularly update dependencies
- Enable Dependabot alerts
- Review third-party code

## Best Practices

### Writing Tests
- Keep tests independent
- Use descriptive test names
- Mock external dependencies
- Test edge cases

### Commit Messages
- Follow Conventional Commits
- Reference issue numbers
- Keep messages concise

## Support

For issues with the CI/CD pipeline:
1. Check the [GitHub Actions documentation](https://docs.github.com/en/actions)
2. Review workflow logs
3. Open an issue in the repository

---

*Last updated: June 2025*
