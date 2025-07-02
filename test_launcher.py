#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for OPRYXX Launcher

This script tests the functionality of the OPRYXX launcher without building the full executable.
"""

import sys
import os
import time
import io
import sys
from pathlib import Path

# Set console output encoding to UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

# Import the launcher module
from opryxx_launcher import OPRYXXLauncher

def test_launcher():
    """Test the OPRYXX launcher functionality."""
    try:
        # Try to print with emoji, fallback to text if encoding fails
        try:
            print("[🚀] Testing OPRYXX Launcher...")
        except UnicodeEncodeError:
            print("[START] Testing OPRYXX Launcher...")
        
        # Create launcher instance
        launcher = OPRYXXLauncher()
        
        # Test starting services
        print("\n[SETUP] Testing service startup...")
        launcher.start_service('api')
        launcher.start_service('monitor')
        
        # Show status
        print("\n[STATUS] Current status:")
        status = launcher.status()
        for service, info in status.items():
            state = "RUNNING" if info['running'] else "STOPPED"
            enabled = "(enabled)" if info['enabled'] else "(disabled)"
            pid = f" [PID: {info['pid']}]" if info['pid'] else ""
            print(f"  {service}: {state} {enabled}{pid}")
        
        # Let services run for a few seconds
        print("\n[WAIT] Letting services run for 5 seconds...")
        time.sleep(5)
        
        # Test stopping services
        print("\n[STOP] Stopping services...")
        launcher.stop_service('monitor')
        launcher.stop_service('api')
        
        print("\n[SUCCESS] Launcher test completed successfully!")
        return True
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_launcher()
