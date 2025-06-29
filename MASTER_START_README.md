# 🚀 OPRYXX MASTER START

Enterprise-Grade System Optimization Suite with One-Click Performance Enhancement

## 🔍 Overview

OPRYXX MASTER START is a comprehensive system optimization tool designed to maximize your computer's performance through automated, intelligent optimizations. Built with enterprise-grade reliability, it combines multiple optimization techniques into a single, easy-to-use interface.

## ✨ Key Features

### 🔍 Comprehensive System Analysis
- **Hardware/Software Inventory**: Detailed system specifications
- **Performance Metrics**: Real-time monitoring of system resources
- **Health Assessment**: Proactive identification of potential issues

### ⚡ High-Power Optimizations
- **Service Optimization**: Disables non-essential background services
- **Power Management**: Optimizes power plans for maximum performance
- **Memory Enhancement**: Advanced cache management and memory optimization
- **Disk Optimization**: Automated cleanup and defragmentation
- **Security Hardening**: Disables vulnerable protocols (SMBv1, LLMNR)

### 🛠️ Enterprise Features
- **Automated Dependency Management**: Ensures all components are up-to-date
- **Version Control**: Built-in version tracking and update notifications
- **Detailed Logging**: Comprehensive operation logs for troubleshooting
- **Error Recovery**: Graceful handling of system errors and interruptions

## 🚀 Getting Started

### Prerequisites
- Windows 10/11 (64-bit)
- Administrator privileges
- 2GB+ free disk space
- .NET Framework 4.7.2 or later

### Installation
1. Download the latest release package
2. Extract the ZIP file to your preferred location
3. Run `OPRYXX_Master_Start.exe` as Administrator

## 🎯 Usage

1. **Launch the Application**
   - Right-click on `OPRYXX_Master_Start.exe`
   - Select "Run as administrator"
   - Click "Yes" on the UAC prompt

2. **Run Optimizations**
   - Click the "START" button
   - View real-time progress and logs
   - Let the process complete (typically 5-15 minutes)

3. **Review Results**
   - View optimization summary
   - Check system health status
   - Review any recommended actions

## ⚙️ Advanced Configuration

### Command Line Options
```
OPRYXX_Master_Start.exe [options]

Basic Options:
  --help, -h           Show this help message and exit
  --version, -v        Show version information and exit
  --silent, -s         Run optimizations without UI (headless mode)
  --log=FILE, -l FILE  Specify custom log file location
  --verbose, -V        Enable verbose output
  --debug, -d          Enable debug mode (includes stack traces)

Optimization Control:
  --skip-scan           Skip the initial system scan
  --optimize=MODULE     Run specific optimization module (comma-separated)
                       Available modules: services, power, memory, disk, security
  --exclude=MODULE      Exclude specific optimization modules
  --force, -f           Force optimizations even if not recommended
  --dry-run, -n         Perform a trial run without making changes

System Configuration:
  --power-plan=PLAN     Set power plan (balanced, high, ultimate, custom)
  --services=ACTION     Set service optimization level (disable, manual, safe, aggressive)
  --cleanup-level=LEVEL Set disk cleanup level (minimal, standard, thorough)
  --security-level=LEVEL Set security level (standard, high, paranoid)

Logging and Output:
  --log-level=LEVEL     Set log level (debug, info, warning, error, critical)
  --output=FORMAT       Set output format (text, json, xml)
  --report=FILE         Generate optimization report to file
  --no-color            Disable colored output

Configuration Management:
  --config=FILE         Specify alternative config file
  --save-config=FILE    Save current configuration to file
  --reset-config        Reset configuration to defaults
  --show-config         Show current configuration and exit

Examples:
  OPRYXX_Master_Start.exe --silent --optimize=memory,disk
  OPRYXX_Master_Start.exe --config=myconfig.ini --log=optimization.log
  OPRYXX_Master_Start.exe --power-plan=ultimate --security-level=high
```

### Configuration File
Create a `config.ini` in the application directory or use `--config` to specify a custom location:

```ini
[System]
# Application settings
language = en_US
check_for_updates = true
auto_update = true
backup_before_changes = true
max_log_size = 10  # MB

[Optimizations]
# Service optimization
optimize_services = true
service_optimization_level = safe  # disable, manual, safe, aggressive

# Power management
optimize_power = true
power_plan = high  # balanced, high, ultimate

# Memory optimization
optimize_memory = true
clear_pagefile_on_exit = false

# Disk optimization
optimize_disk = true
defrag_type = standard  # quick, standard, thorough
cleanup_temp = true
cleanup_windows_update = true
cleanup_browser_cache = true

# Security hardening
harden_security = true
security_level = standard  # standard, high, paranoid

[UI]
# Interface settings
theme = dark  # dark, light, system
font_size = 10
font_family = Segoe UI
show_splash = true
minimize_to_tray = true
close_to_tray = false

[Logging]
# Logging configuration
log_level = info  # debug, info, warning, error, critical
log_to_file = true
log_file = %PROGRAMDATA%\OPRYXX\master_start.log
max_log_files = 5

[Network]
# Network-related settings
use_proxy = false
proxy_address = 
proxy_port = 
proxy_username = 
proxy_password = 

[Advanced]
# Advanced settings (use with caution)
enable_experimental = false
enable_telemetry = false
enable_crash_reports = true

[Performance]
# Performance tuning
max_threads = auto  # auto or number
memory_limit = 80%  # 0-100% or specific value in MB
disk_io_priority = normal  # low, normal, high

[Exclusions]
# Exclude specific items from optimization
services_exclude = 
disks_exclude = 
paths_exclude = 

[Backup]
# Backup configuration
backup_enabled = true
backup_location = %APPDATA%\OPRYXX\backups
backup_count = 5
backup_compression = zip  # none, zip, 7z

[Notifications]
# Notification settings
notify_completion = true
notify_errors = true
toast_notifications = true
sound_notifications = true

[AutoRun]
# Schedule automatic optimizations
enabled = false
schedule = weekly  # daily, weekly, monthly
frequency = 1  # Number of schedule units
day_of_week = sunday  # For weekly schedule
time = 02:00
run_on_battery = false

[Modules]
# Enable/disable specific modules
module_services = true
module_power = true
module_memory = true
module_disk = true
module_security = true
module_network = true
module_registry = true
module_startup = true
```

### Environment Variables
You can also configure the application using environment variables (they take precedence over config file):

```
# General
OPRYXX_CONFIG=path/to/config.ini
OPRYXX_LOG_LEVEL=debug
OPRYXX_THEME=dark

# Optimization Settings
OPRYXX_OPTIMIZE_MEMORY=true
OPRYXX_OPTIMIZE_DISK=true
OPRYXX_POWER_PLAN=high
OPRYXX_SECURITY_LEVEL=standard

# Network
HTTP_PROXY=http://proxy:port
HTTPS_PROXY=http://proxy:port
NO_PROXY=localhost,127.0.0.1
```

### Registry Settings (Windows)
Advanced users can configure settings via Windows Registry:
```
HKEY_CURRENT_USER\Software\OPRYXX\MasterStart
```

### Configuration Precedence
1. Command-line arguments (highest priority)
2. Environment variables
3. Configuration file (config.ini)
4. Registry settings
5. Default values (lowest priority)

## 🚀 Build and Automation System

This project features a comprehensive build and automation system designed to streamline development, testing, and deployment processes. The system is built around a powerful `Makefile` and modern Python tooling.

### 🛠️ Key Features

- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **One-Command Setup**: Get started quickly with `make dev-setup`
- **Automated Testing**: Run tests with coverage and generate reports
- **Code Quality**: Enforce consistent code style and catch issues early
- **Containerization**: Docker support for development and production
- **CI/CD Ready**: Pre-configured for GitHub Actions

### 🚦 Quick Start

1. **Set up the development environment**:
   ```bash
   make dev-setup
   ```

2. **Run tests**:
   ```bash
   make test
   ```

3. **Build the package**:
   ```bash
   make build
   ```

4. **Run locally**:
   ```bash
   make run
   ```

### 🔍 Development Commands

| Command | Description |
|---------|-------------|
| `make dev-setup` | Set up development environment |
| `make dev-shell` | Start development shell |
| `make dev-test` | Run development tests |
| `make dev-lint` | Run linters |
| `make dev-format` | Format code |

### 🧪 Testing

| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make test-unit` | Run unit tests |
| `make test-integration` | Run integration tests |
| `make test-e2e` | Run end-to-end tests |
| `make test-coverage` | Generate coverage report |
| `make test-html` | Generate HTML coverage report |

### 🧹 Code Quality

| Command | Description |
|---------|-------------|
| `make lint` | Run all linters |
| `make format` | Format code |
| `make check-format` | Check code formatting |
| `make check-all` | Run all checks |

### 🐳 Docker

| Command | Description |
|---------|-------------|
| `make docker-build` | Build Docker image |
| `make docker-run` | Run Docker container |
| `make compose-up` | Start services with Docker Compose |
| `make compose-down` | Stop services |
| `make compose-logs` | View service logs |

### 🚀 Deployment

| Command | Description |
|---------|-------------|
| `make deploy-staging` | Deploy to staging |
| `make deploy-production` | Deploy to production |
| `make deploy-rollback` | Rollback deployment |

### 🔄 Release Management

| Command | Description |
|---------|-------------|
| `make release-major` | Create major release |
| `make release-minor` | Create minor release |
| `make release-patch` | Create patch release |
| `make bump-version` | Bump version (major.minor.patch) |

### 🧹 Cleanup

| Command | Description |
|---------|-------------|
| `make clean` | Remove Python file artifacts |
| `make clean-all` | Remove all build artifacts |
| `make docker-clean` | Clean Docker resources |

## 🚀 GitHub Actions Workflows

This project uses GitHub Actions for CI/CD, testing, and automation. Below is a summary of the available workflows:

### Core Workflows

#### 1. CI/CD Pipeline (`.github/workflows/ci-cd-consolidated.yml`)
- **Purpose**: Main workflow that runs on every push and pull request
- **Features**:
  - Runs unit tests with coverage
  - Performs security scanning
  - Runs performance tests
  - Builds and deploys the application
  - Generates and publishes documentation
- **Triggers**: `push`, `pull_request`, `workflow_dispatch`
- **Secrets Required**: `CODECOV_TOKEN`

#### 2. Security Scan (`.github/workflows/security-scan.yml`)
- **Purpose**: Runs security checks on the codebase
- **Features**:
  - Bandit security linter
  - Safety dependency checker
  - TruffleHog secret scanning
  - Gitleaks for secrets detection
  - Semgrep for static analysis
- **Triggers**: `push`, `pull_request`, `schedule`, `workflow_dispatch`
- **Frequency**: Weekly on Sunday

#### 3. Dependency Management (`.github/workflows/dependencies.yml`)
- **Purpose**: Manages and updates project dependencies
- **Features**:
  - Updates Python dependencies
  - Checks for security vulnerabilities
  - Generates Software Bill of Materials (SBOM)
  - Creates PRs for dependency updates
- **Triggers**: `schedule`, `workflow_dispatch`
- **Secrets Used**: `SNYK_TOKEN`

### Auxiliary Workflows

#### 4. End-to-End Testing (`.github/workflows/e2e-testing.yml`)
- **Purpose**: Runs comprehensive end-to-end tests
- **Features**:
  - Cross-platform testing (Windows, Linux, macOS)
  - Multiple Python version support
  - Test result artifact uploads
  - Coverage reporting
- **Triggers**: `push`, `pull_request`, `workflow_dispatch`

#### 5. Error Recovery (`.github/workflows/error-recovery.yml`)
- **Purpose**: Monitors system health and recovers from errors
- **Features**:
  - System health checks
  - Automatic recovery actions
  - Slack notifications
  - Issue creation for critical errors
- **Triggers**: `schedule`, `workflow_dispatch`
- **Secrets Used**: `SLACK_WEBHOOK`

#### 6. Release Management (`.github/workflows/release.yml`)
- **Purpose**: Handles versioned releases
- **Features**:
  - Automated version bumping
  - PyPI package publishing
  - GitHub release creation
  - Changelog generation
- **Triggers**: `push` (tags), `workflow_dispatch`
- **Secrets Used**: `PYPI_API_TOKEN`

### Workflow Configuration

#### Environment Variables
- `CODECOV_TOKEN`: For code coverage reporting
- `SNYK_TOKEN`: For vulnerability scanning
- `SLACK_WEBHOOK`: For notifications
- `PYPI_API_TOKEN`: For PyPI package publishing
- `GITHUB_TOKEN`: Automatically provided by GitHub

#### Scheduled Jobs
- Security scans: Weekly on Sunday
- Dependency updates: Weekly on Sunday
- Health checks: Hourly

### Customizing Workflows

1. **Modifying Schedules**:
   Edit the cron expressions in the respective workflow files.

2. **Adding New Jobs**:
   Follow the existing pattern in the workflow files, ensuring proper `needs` and `if` conditions.

3. **Debugging**:
   - Enable debugging by adding `ACTIONS_STEP_DEBUG: true` to the workflow environment
   - Check the "Actions" tab in GitHub for detailed logs

### Best Practices

1. **Secret Management**:
   - Never hardcode secrets in workflow files
   - Use GitHub Secrets for sensitive data
   - Limit secret access to required workflows

2. **Performance**:
   - Use caching for dependencies
   - Run jobs in parallel when possible
   - Use appropriate runner sizes

3. **Maintenance**:
   - Keep actions up to date
   - Regularly review and update dependencies
   - Monitor workflow durations and optimize as needed

## 🛠 Troubleshooting

### Common Issues
- **Windows Defender Warning**: 
  - Click "More info" then "Run anyway"
  - Add the executable to Windows Defender exclusions if needed

- **Performance Issues**:
  - Close other applications before running
  - Ensure adequate free disk space
  - Run disk cleanup manually if needed

### Logs
Detailed logs are available at:
```
%PROGRAMDATA%\OPRYXX\master_start.log
```

## 📜 License

Copyright © 2025 OPRYXX Systems. All rights reserved.

## 📞 Support

For support or feature requests, please contact:
- Email: support@opryxx.systems
- Website: https://opryxx.systems

---

**Version:** 2.0.0 | **Build Date:** 2025-06-27
