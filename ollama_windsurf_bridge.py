"""
Ollama Windsurf Bridge - Enhanced Integration
Based on your repository patterns
"""

import requests
import json
from typing import Dict, List

class OllamaWindsurfBridge:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.active_model = "llama2"
        
    def code_analysis(self, code: str) -> str:
        """Analyze code using Ollama"""
        prompt = f"Analyze this code and suggest improvements:\n{code}"
        return self._chat(prompt, "codellama")
    
    def legal_query(self, query: str) -> str:
        """Legal assistance using Ollama"""
        prompt = f"Legal query: {query}\nProvide brief guidance:"
        return self._chat(prompt, "llama2")
    
    def research_assistant(self, topic: str) -> str:
        """Research assistant functionality"""
        prompt = f"Research topic: {topic}\nProvide key insights:"
        return self._chat(prompt, "llama2")
    
    def _chat(self, prompt: str, model: str = None) -> str:
        """Core chat functionality"""
        try:
            response = requests.post(f"{self.base_url}/api/generate",
                json={
                    "model": model or self.active_model,
                    "prompt": prompt,
                    "stream": False
                }, timeout=30)
            
            if response.status_code == 200:
                return response.json().get("response", "No response")
            return "Error: API call failed"
        except Exception as e:
            return f"Error: {str(e)}"

# Global bridge instance
ollama_bridge = OllamaWindsurfBridge()