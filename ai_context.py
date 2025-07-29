from sentence_transformers import SentenceTransformer
import pickle
import os

CONTEXT_FILE = "ai_context.pkl"

def initialize():
    """Initialize the AI context with default knowledge"""
    if not os.path.exists(CONTEXT_FILE):
        base_knowledge = {
            "system_commands": ["git", "docker", "python", "node"],
            "project_knowledge": ["OPRYXX system", "PC repair", "AI optimization"],
            "conversation_history": []
        }
        with open(CONTEXT_FILE, "wb") as f:
            pickle.dump(base_knowledge, f)

def get_context(query):
    """Retrieve relevant context for a query"""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    with open(CONTEXT_FILE, "rb") as f:
        knowledge = pickle.load(f)

    # Basic context matching (would be enhanced in production)
    if "run" in query.lower() or "execute" in query.lower():
        return "CommandMode: " + ", ".join(knowledge["system_commands"])
    return "GeneralMode"
