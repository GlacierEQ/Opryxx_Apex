import os
from sentence_transformers import SentenceTransformer
import pandas as pd

class AIFileSystem:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def analyze_file(self, path):
        """Analyze file content intelligently"""
        if not os.path.exists(path):
            return f"File not found: {path}"

        if os.path.isdir(path):
            files = [f for f in os.listdir(path) if not f.startswith('.')]
            return f"Directory contents: {', '.join(files)}"

        # Simple content analysis
        with open(path, 'r') as f:
            content = f.read(1000)  # First 1000 chars

        embedding = self.model.encode(content)
        return {
            'path': path,
            'summary': f"Content analyzed with {len(content)} characters",
            'embedding': embedding
        }

def analyze_file(path):
    aifs = AIFileSystem()
    return aifs.analyze_file(path)
