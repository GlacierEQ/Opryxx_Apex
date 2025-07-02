#!/usr/bin/env python3
"""
Test script for OPRYXX Launcher

This script tests the functionality of the OPRYXX launcher without building the full executable.
"""

import sys
import os
import time
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

# Import the launcher module
from opryxx_launcher import OPRYXXLauncher

def test_launcher():
    """Test the OPRYXX launcher functionality."""
    print("🚀 Testing OPRYXX Launcher...")
    
    # Create launcher instance
    launcher = OPRYXXLauncher()
    
    # Test starting services
    print("\n🔧 Testing service startup...")
    launcher.start_service('api')
    launcher.start_service('monitor')
    
    # Show status
    print("\n📊 Current status:")
    status = launcher.status()
    for service, info in status.items():
        state = "RUNNING" if info['running'] else "STOPPED"
        enabled = "(enabled)" if info['enabled'] else "(disabled)"
        pid = f" [PID: {info['pid']}]" if info['pid'] else ""
        print(f"  {service}: {state} {enabled}{pid}")
    
    # Let services run for a few seconds
    print("\n⏳ Letting services run for 5 seconds...")
    time.sleep(5)
    
    # Test stopping services
    print("\n🛑 Stopping services...")
    launcher.stop_service('monitor')
    launcher.stop_service('api')
    
    print("\n✅ Launcher test completed successfully!")

if __name__ == "__main__":
    test_launcher()
