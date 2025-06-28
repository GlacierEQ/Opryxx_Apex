"""
Input Validation and Security for OPRYXX API
"""

import re
from typing import Any, Dict, List
from dataclasses import dataclass

@dataclass
class ValidationRule:
    field: str
    required: bool = True
    max_length: int = None
    min_length: int = None
    pattern: str = None
    allowed_values: List[str] = None

class InputValidator:
    def __init__(self):
        self.dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__',
            r'subprocess',
            r'os\.system',
            r'\.\./',
            r'<iframe',
            r'<object',
            r'<embed'
        ]
    
    def validate_request(self, data: Dict, rules: List[ValidationRule]) -> Dict:
        """Validate request data against rules"""
        errors = []
        
        for rule in rules:
            value = data.get(rule.field)
            
            # Check required fields
            if rule.required and (value is None or value == ""):
                errors.append(f"{rule.field} is required")
                continue
            
            if value is None:
                continue
            
            # Check string length
            if isinstance(value, str):
                if rule.max_length and len(value) > rule.max_length:
                    errors.append(f"{rule.field} exceeds maximum length of {rule.max_length}")
                
                if rule.min_length and len(value) < rule.min_length:
                    errors.append(f"{rule.field} below minimum length of {rule.min_length}")
                
                # Check pattern
                if rule.pattern and not re.match(rule.pattern, value):
                    errors.append(f"{rule.field} does not match required pattern")
                
                # Check for dangerous content
                if not self.is_safe_input(value):
                    errors.append(f"{rule.field} contains potentially dangerous content")
            
            # Check allowed values
            if rule.allowed_values and value not in rule.allowed_values:
                errors.append(f"{rule.field} must be one of: {', '.join(rule.allowed_values)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def is_safe_input(self, input_str: str) -> bool:
        """Check if input is safe from injection attacks"""
        input_lower = input_str.lower()
        
        for pattern in self.dangerous_patterns:
            if re.search(pattern, input_lower, re.IGNORECASE):
                return False
        
        return True
    
    def sanitize_input(self, input_str: str) -> str:
        """Sanitize input string"""
        # Remove dangerous characters
        sanitized = re.sub(r'[<>"\']', '', input_str)
        
        # Limit length
        sanitized = sanitized[:1000]
        
        # Remove control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32)
        
        return sanitized.strip()

# Common validation rules
QUERY_RULES = [
    ValidationRule("prompt", required=True, max_length=1000),
    ValidationRule("temperature", required=False),
    ValidationRule("max_tokens", required=False)
]

RECOVERY_RULES = [
    ValidationRule("operation", required=True, allowed_values=["safe_mode_exit", "boot_repair", "system_check"]),
    ValidationRule("force", required=False, allowed_values=["true", "false"])
]

OPTIMIZATION_RULES = [
    ValidationRule("mode", required=False, allowed_values=["balanced", "performance", "ultra", "extreme"]),
    ValidationRule("target", required=False, allowed_values=["memory", "cpu", "disk", "all"])
]