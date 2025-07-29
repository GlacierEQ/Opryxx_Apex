from sentence_transformers import SentenceTransformer
import subprocess
import numpy as np
from windsurf_ollama_hook import windsurf_ollama
from ollama_windsurf_bridge import ollama_bridge

class TaskAnalyzer:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.command_embeddings = {
            "git": self.model.encode("version control operations"),
            "docker": self.model.encode("container management"),
            "python": self.model.encode("run python scripts"),
            "ls": self.model.encode("list directory contents")
        }

    def analyze_task(self, query_embedding):
        """Convert natural language to executable command"""
        # Find most similar command
        similarities = {
            cmd: np.dot(embed, query_embedding)
            for cmd, embed in self.command_embeddings.items()
        }
        best_match = max(similarities, key=similarities.get)

        if "list" in best_match:
            return "Get-ChildItem"
        return best_match
    
    def chat_with_ollama(self, query: str) -> str:
        """Chat with Ollama AI"""
        return ollama_bridge._chat(query)
    
    def analyze_code_with_ollama(self, code: str) -> str:
        """Analyze code with Ollama"""
        return ollama_bridge.code_analysis(code)
    
    def research_with_ollama(self, topic: str) -> str:
        """Research with Ollama"""
        return ollama_bridge.research_assistant(topic)

def analyze_task(query):
    analyzer = TaskAnalyzer()
    return analyzer.analyze_task(query)
