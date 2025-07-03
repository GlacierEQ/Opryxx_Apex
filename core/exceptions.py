"""
Custom exceptions for OPRYXX
"""

class OPRYXXException(Exception):
    """Base exception for OPRYXX"""
    pass

class ModuleException(OPRYXXException):
    """Exception for module-related errors"""
    pass

class ConfigurationException(OPRYXXException):
    """Exception for configuration errors"""
    pass

class RecoveryException(OPRYXXException):
    """Exception for recovery operations"""
    pass

class HardwareException(OPRYXXException):
    """Exception for hardware-related errors"""
    pass

class SecurityException(OPRYXXException):
    """Exception for security-related errors"""
    pass