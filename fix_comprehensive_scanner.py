"""
Fix Comprehensive System Scanner - Remove unused imports and fix errors
"""

import re

def fix_scanner_file():
    """Fix all issues in comprehensive_system_scanner.py"""
    file_path = "ai/comprehensive_system_scanner.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove unused imports
    unused_imports = [
        "import signal",
        "import tempfile", 
        "from collections import defaultdict",
        "from datetime import timedelta",
        "from pathlib import Path",
        "from typing import Tuple",
        "from typing import Union"
    ]
    
    for imp in unused_imports:
        content = content.replace(imp + "\n", "")
    
    # Fix Microsoft undefined error
    content = content.replace("Microsoft", '"Microsoft"')
    
    # Add requests import
    if "import requests" not in content:
        content = content.replace("import psutil", "import psutil\nimport requests")
    
    # Fix line length issues (basic fixes)
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if len(line) > 79:
            # Simple line break for long lines
            if ' and ' in line and len(line) > 100:
                parts = line.split(' and ')
                if len(parts) == 2:
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(parts[0] + ' and')
                    fixed_lines.append(' ' * (indent + 4) + parts[1])
                    continue
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Remove trailing whitespace and fix blank lines
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Remove trailing whitespace
        line = line.rstrip()
        # Fix blank lines with whitespace
        if line.strip() == '':
            line = ''
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Add blank lines before functions/classes
    content = re.sub(r'\n(def |class )', r'\n\n\1', content)
    content = re.sub(r'\n\n\n(def |class )', r'\n\n\1', content)  # Remove triple newlines
    
    # Fix regex escape sequences
    content = content.replace(r'\.', r'\.')
    content = content.replace(r'\s', r'\\s')
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("Fixed comprehensive_system_scanner.py")

if __name__ == "__main__":
    fix_scanner_file()