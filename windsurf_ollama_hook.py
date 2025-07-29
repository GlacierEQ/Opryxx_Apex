"""
Windsurf IDE Ollama Integration Hook
Connects Ollama to the global IDE environment
"""

import requests
import json
import subprocess
from typing import Dict, Optional

class WindsurfOllamaHook:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.active = False
        
    def setup_ollama(self):
        """Setup Ollama in Windsurf IDE"""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            self.active = True
            return True
        except:
            # Start Ollama if not running
            try:
                subprocess.Popen(["ollama", "serve"], shell=True)
                self.active = True
                return True
            except:
                return False
    
    def chat_with_code(self, code: str, question: str) -> str:
        """Chat about code with Ollama"""
        if not self.active:
            return "Ollama not available"
            
        prompt = f"Code:\n{code}\n\nQuestion: {question}"
        
        try:
            response = requests.post(f"{self.ollama_url}/api/generate", 
                json={
                    "model": "codellama",
                    "prompt": prompt,
                    "stream": False
                })
            return response.json()["response"]
        except:
            return "Error communicating with Ollama"
    
    def optimize_code(self, code: str) -> str:
        """Get code optimization suggestions"""
        prompt = f"Optimize this code:\n{code}"
        
        try:
            response = requests.post(f"{self.ollama_url}/api/generate",
                json={
                    "model": "codellama", 
                    "prompt": prompt,
                    "stream": False
                })
            return response.json()["response"]
        except:
            return "Error getting optimization suggestions"

# Global hook instance
windsurf_ollama = WindsurfOllamaHook()
windsurf_ollama.setup_ollama()