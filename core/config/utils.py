""
Configuration Utilities
Helper functions for common configuration tasks
"""
    """
    """
            raise ValueError(f"Failed to load configuration from {config_path}")
        
        # Validate against schema
        config_dict = config.to_dict()
        return schema(**config_dict)
        
    except ValidationError as e:
        logger.error(f"Configuration validation failed: {str(e)}")
        raise ValueError(f"Invalid configuration: {str(e)}") from e
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        raise

def find_config_file(filename: str, 
                   search_paths: Optional[list] = None,
                   raise_if_not_found: bool = True) -> Optional[str]:
    """
    """
        os.path.expanduser("~/.config/opryxx"),  # User config dir
        "/etc/opryxx",  # System config dir
        os.path.dirname(os.path.abspath(__file__)),  # Package dir
    ]
    
    # Add custom search paths if provided
    search_paths = (search_paths or []) + default_paths
    
    # Check each path
    for path in search_paths:
        full_path = os.path.join(path, filename)
        if os.path.isfile(full_path):
            return os.path.abspath(full_path)
    
    # File not found
    if raise_if_not_found:
        raise FileNotFoundError(
            f"Could not find config file '{filename}' in any of: {', '.join(search_paths)}"
        )
    return None

def get_environment_config(prefix: str = "OPRYXX") -> dict:
    """
    """
    """
    """
    """
    """
    logger.info("Logging configured")

def get_typed_config(section: str, 
                   config_type: Type[T],
                   config: Optional[ConfigManager] = None) -> T:
    """
    """
        logger.error(f"Invalid configuration for section '{section}': {str(e)}")
        raise ValueError(f"Invalid configuration for section '{section}'") from e

"""