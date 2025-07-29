"""
Windsurf IDE Global Startup - Auto-load on IDE start
"""

import sys
import os

# Add OPRYXX to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import and activate global integration
try:
    from windsurf_global_integration import windsurf_global
    print("✅ OPRYXX Global Integration Active")
except Exception as e:
    print(f"❌ Integration failed: {e}")

# Auto-start Ollama if available
try:
    from start_ollama import start_ollama
    start_ollama()
    print("✅ Ollama Server Started")
except:
    print("⚠️ Ollama not started")

print("🚀 Windsurf IDE Maximum Integration Complete")