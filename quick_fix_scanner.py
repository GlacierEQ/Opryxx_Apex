"""
Quick fix for comprehensive system scanner - minimal changes
"""

def quick_fix():
    """Apply minimal fixes to comprehensive_system_scanner.py"""
    file_path = "ai/comprehensive_system_scanner.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except:
        with open(file_path, 'r', encoding='latin-1') as f:
            lines = f.readlines()
    
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Remove unused imports
        if any(x in line for x in ["import signal", "import tempfile", "from collections import defaultdict", 
                                  "from datetime import timedelta", "from pathlib import Path", 
                                  "from typing import Tuple", "from typing import Union"]):
            continue
            
        # Fix Microsoft undefined
        if "Microsoft" in line and '"Microsoft"' not in line:
            line = line.replace("Microsoft", '"Microsoft"')
            
        # Add requests import after psutil
        if "import psutil" in line and "import requests" not in ''.join(lines):
            fixed_lines.append(line)
            fixed_lines.append("import requests\n")
            continue
            
        # Remove trailing whitespace
        line = line.rstrip() + '\n'
        
        # Fix blank lines with whitespace
        if line.strip() == '':
            line = '\n'
            
        fixed_lines.append(line)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("Quick fix applied to comprehensive_system_scanner.py")

if __name__ == "__main__":
    quick_fix()