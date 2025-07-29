from sentence_transformers import SentenceTransformer
import subprocess
import numpy as np

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

def analyze_task(query):
    analyzer = TaskAnalyzer()
    return analyzer.analyze_task(query)
