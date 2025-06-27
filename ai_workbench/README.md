# AI Workbench

Advanced system monitoring and optimization tool with AI capabilities for the OPRYXX system.

## Features

- **System Monitoring**: Real-time monitoring of CPU, memory, disk, and network usage
- **Performance Optimization**: Automated system optimization based on usage patterns
- **Predictive Analysis**: AI-powered failure prediction and prevention
- **Customizable Alerts**: Configurable notifications for system events
- **Extensible Architecture**: Plugin system for adding new monitoring and optimization modules

## Installation

1. Ensure you have Python 3.7 or higher installed
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Install the AI Workbench in development mode:

```bash
pip install -e .
```

## Configuration

1. Copy the example configuration file:

```bash
cp config/example_config.json config/config.json
```

2. Edit the configuration file to match your system settings.

## Usage

### Command Line

```bash
# Start the AI Workbench
python -m ai_workbench

# With custom config
python -m ai_workbench --config /path/to/config.json

# Enable verbose logging
python -m ai_workbench --verbose
```

### As a Module

```python
from ai_workbench import AIWorkbench

# Create and start the workbench
workbench = AIWorkbench()
workbench.start()
```

## Directory Structure

```
ai_workbench/
├── __init__.py           # Package initialization
├── __main__.py          # Main entry point
├── config.py            # Configuration management
├── models/              # Database models
│   ├── __init__.py
│   └── workbench_models.py
├── services/            # Business logic
│   ├── __init__.py
│   ├── database_service.py
│   └── workbench_service.py
└── utils/               # Utility modules
    ├── __init__.py
    ├── logging_utils.py
    └── system_utils.py
```

## Development

### Setting Up Development Environment

1. Clone the repository
2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

### Running Tests

```bash
pytest tests/
```

### Code Style

This project uses:
- Black for code formatting
- isort for import sorting
- flake8 for linting

Run the following commands before committing:

```bash
black .
isort .
flake8
```

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) before submitting pull requests.

## Support

For support, please open an issue in the issue tracker.

---

*This project is part of the OPRYXX system.*
