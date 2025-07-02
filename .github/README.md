# GitHub Actions Workflows

This repository contains a comprehensive set of GitHub Actions workflows designed for maximum automation and code quality.

## 🚀 Available Workflows

### Core Workflows
- **`main-ci.yml`** - Main CI/CD pipeline with testing, building, and deployment
- **`reusable-ci.yml`** - Reusable workflow template for other repositories
- **`multi-platform.yml`** - Cross-platform testing (Windows, macOS, Linux)

### Quality & Security
- **`code-quality.yml`** - Code formatting, linting, type checking, complexity analysis
- **`security-scan.yml`** - Security scanning with Bandit, Safety, Semgrep, CodeQL
- **`performance-monitoring.yml`** - Performance testing and GPU acceleration tests

### Automation
- **`dependency-update.yml`** - Automated dependency updates with security audits
- **`auto-release.yml`** - Automated releases with changelog generation
- **`docs-deploy.yml`** - Documentation building and deployment to GitHub Pages
- **`template-sync.yml`** - Sync workflows across multiple repositories

## 🔧 Setup Instructions

### 1. Repository Secrets
Add these secrets to your repository settings:

```
GITHUB_TOKEN          # Automatically provided by GitHub
DOCKERHUB_USERNAME    # Your Docker Hub username
DOCKERHUB_TOKEN       # Your Docker Hub access token
SYNC_TOKEN           # Personal access token for template sync
```

### 2. Enable GitHub Pages
1. Go to Settings → Pages
2. Select "GitHub Actions" as source
3. Documentation will be automatically deployed

### 3. Configure Branch Protection
Recommended branch protection rules for `main`:
- Require pull request reviews
- Require status checks to pass
- Require branches to be up to date
- Include administrators

## 📋 Workflow Features

### Reusable Workflows
The `reusable-ci.yml` can be used across multiple repositories:

```yaml
jobs:
  ci:
    uses: your-org/OPRYXX_LOGS/.github/workflows/reusable-ci.yml@main
    with:
      python-version: '3.11'
      run-tests: true
      run-security-scan: true
      run-performance-tests: false
```

### Multi-Platform Testing
Tests run on:
- Ubuntu Latest
- Windows Latest  
- macOS Latest
- Python 3.9, 3.10, 3.11

### Security Scanning
Multiple security tools:
- **Bandit** - Python security linter
- **Safety** - Dependency vulnerability scanner
- **Semgrep** - Static analysis security scanner
- **CodeQL** - GitHub's semantic code analysis

### Performance Monitoring
- Benchmark testing with pytest-benchmark
- Memory profiling
- GPU acceleration testing (with CPU fallback)
- Performance regression detection

## 🔄 Template Sync

Use the template sync workflow to propagate updates across repositories:

1. Trigger manually with target repository
2. Automatically runs weekly
3. Creates PR with updated workflows
4. Maintains consistency across projects

## 📊 Code Quality Tools

Configured tools:
- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking
- **pylint** - Advanced linting
- **radon** - Complexity analysis

## 🚀 Getting Started

1. Copy workflows to your repository's `.github/workflows/`
2. Copy configuration files (`.bandit`, `pyproject.toml`, `mkdocs.yml`)
3. Set up repository secrets
4. Enable GitHub Pages
5. Configure branch protection
6. Push changes to trigger workflows

## 📈 Monitoring

All workflows generate artifacts and reports:
- Test coverage reports
- Security scan results
- Performance benchmarks
- Code quality metrics
- Build artifacts

Access these in the Actions tab of your repository.

## 🔧 Customization

Each workflow can be customized by:
- Modifying trigger conditions
- Adjusting tool configurations
- Adding/removing steps
- Changing matrix strategies

See individual workflow files for specific configuration options.