"""
Ollama Integration for OPRYXX - Global Windsurf IDE Hook
Minimal integration to connect Ollama AI models with the system
"""

import requests
import json
import asyncio
from typing import Dict, List, Optional

class OllamaIntegration:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.active_model = None
        
    async def chat(self, prompt: str, model: str = "llama2") -> str:
        """Send chat request to Ollama"""
        try:
            response = requests.post(f"{self.base_url}/api/chat", 
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                })
            return response.json()["message"]["content"]
        except Exception as e:
            return f"Ollama error: {str(e)}"
    
    def get_models(self) -> List[str]:
        """Get available Ollama models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return [model["name"] for model in response.json()["models"]]
        except:
            return []

# Global Ollama instance
ollama = OllamaIntegration()

# Hook into pipelines.py
def integrate_ollama_commands():
    """Add Ollama commands to the pipeline system"""
    return {
        "ai_chat": {
            "command": "ollama_chat",
            "executable": True,
            "gui_action": "launch_ai_chat",
            "parameters": {"model": "llama2"}
        },
        "code_review": {
            "command": "ollama_code_review", 
            "executable": True,
            "gui_action": "launch_code_review",
            "parameters": {"model": "codellama"}
        }
    }