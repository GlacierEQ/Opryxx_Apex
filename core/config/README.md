# OPRYXX Configuration System

A unified configuration management system for the OPRYXX platform, supporting multiple formats, environment variable overrides, and hot-reloading.

## Features

- **Multiple Formats**: Support for YAML, JSON, and TOML configuration files
- **Environment Variable Overrides**: Easily override any setting with environment variables
- **Hot-Reloading**: Automatic reloading of configuration files when they change
- **Type Safety**: Built-in validation using Pydantic models
- **Hierarchical Configuration**: Support for nested configuration sections
- **Unified Interface**: Consistent API for accessing configuration values

## Installation

Add the following to your `requirements.txt`:

```
pyyaml>=6.0.1
tomli>=2.0.1
watchdog>=3.0.0
```

## Basic Usage

### Loading Configuration

```python
from core.config import ConfigManager, ConfigFormat

# Create a config manager instance
config = ConfigManager()

# Add a configuration source
config.add_source(
    path="config/settings.yaml",
    format=ConfigFormat.YAML,
    env_prefix="APP_"  # Optional: prefix for environment variable overrides
)

# Access configuration values
host = config["database.host"]
port = config["database.port"]

# With default value
timeout = config.get("database.timeout", default=30)
```

### Using Environment Variables

Environment variables can override any configuration value. Use double underscores (`__`) for nested keys:

```bash
# Override database.host and database.port
APP_DATABASE__HOST=localhost
APP_DATABASE__PORT=5432
```

### Schema Validation

Define your configuration schema using Pydantic models:

```python
from pydantic import BaseModel, PositiveInt

class DatabaseConfig(BaseModel):
    host: str
    port: PositiveInt
    name: str
    user: str
    password: str
    pool_size: int = 10

# Load and validate config
from core.config.utils import load_config_schema

db_config = load_config_schema(
    "config/database.yaml",
    schema=DatabaseConfig,
    env_prefix="DB_"
)
```

### Watching for Changes

```python
# Add a source with watch enabled
config.add_source(
    path="config/settings.yaml",
    format=ConfigFormat.YAML,
    watch=True  # Enable file watching
)

# Subscribe to configuration changes
def on_config_changed(event):
    print(f"Config changed: {event.source}")
    print(f"New value: {event.data}")

config.subscribe(on_config_changed)
```

## Advanced Usage

### Multiple Configuration Sources

```python
# Load multiple configuration sources
config.add_source("config/defaults.yaml", ConfigFormat.YAML)
config.add_source("config/local.yaml", ConfigFormat.YAML, required=False)
config.add_source("config/secrets.json", ConfigFormat.JSON, required=True)
```

### Custom Configuration Sources

```python
from core.config import ConfigSource, ConfigFormat

# Create a custom configuration source
custom_source = ConfigSource(
    path="path/to/config.toml",
    format=ConfigFormat.TOML,
    required=True,
    watch=True,
    env_prefix="CUSTOM_"
)

config.add_source(custom_source)
```

### Logging Configuration

```python
from core.config.utils import configure_logging

# Configure logging from a config dictionary
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard"
        }
    },
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        }
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True
        }
    }
}

configure_logging(logging_config)
```

## Best Practices

1. **Use Environment Variables for Secrets**: Never commit sensitive information to version control.
2. **Validate Early**: Validate configuration at application startup.
3. **Use Meaningful Names**: Use descriptive names for configuration keys.
4. **Document Defaults**: Document default values in your configuration schemas.
5. **Handle Missing Values**: Always provide sensible defaults for optional configuration.

## API Reference

### `ConfigManager`

- `add_source(source: Union[str, ConfigSource], **kwargs) -> bool`: Add a configuration source
- `get(key: str, default: Any = None) -> Any`: Get a configuration value with optional default
- `__getitem__(key: str) -> Any`: Get a configuration value (raises KeyError if not found)
- `get_section(section: str) -> dict`: Get a configuration section as a dictionary
- `to_dict() -> dict`: Get the entire configuration as a dictionary
- `validate(schema: Type[BaseModel]) -> bool`: Validate the configuration against a Pydantic schema
- `subscribe(callback: Callable[[ConfigUpdateEvent], None])`: Subscribe to configuration changes
- `unsubscribe(callback: Callable[[ConfigUpdateEvent], None])`: Unsubscribe from configuration changes
- `reload() -> bool`: Reload all configuration sources

### `ConfigSource`

- `path: str`: Path to the configuration file
- `format: ConfigFormat`: Configuration format (YAML, JSON, TOML)
- `required: bool = True`: Whether the source is required
- `watch: bool = False`: Whether to watch for file changes
- `env_prefix: Optional[str] = None`: Prefix for environment variable overrides

### `ConfigFormat`

Enum of supported configuration formats:
- `YAML`
- `JSON`
- `TOML`

## License

This project is part of the OPRYXX platform. See the main LICENSE file for licensing information.
