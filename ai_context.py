from sentence_transformers import SentenceTransformer
import pickle
import os
from datetime import datetime

CONTEXT_FILE = "ai_context.pkl"
CHAT_LOG_DIR = "chat_logs"

def initialize():
    """Initialize the AI context with default knowledge"""
    if not os.path.exists(CHAT_LOG_DIR):
        os.makedirs(CHAT_LOG_DIR)
        
    if not os.path.exists(CONTEXT_FILE):
        base_knowledge = {
            "system_commands": ["git", "docker", "python", "node", "powershell"],
            "project_knowledge": ["OPRYXX system", "PC repair", "AI optimization"],
            "conversation_history": [],
            "last_context": ""
        }
        with open(CONTEXT_FILE, "wb") as f:
            pickle.dump(base_knowledge, f)

def get_context(query):
    """Retrieve and update context for a query"""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    with open(CONTEXT_FILE, "rb") as f:
        knowledge = pickle.load(f)
    
    # Update conversation history
    knowledge["conversation_history"].append({
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "context": knowledge["last_context"]
    })
    
    # Enhanced context matching
    if any(cmd in query.lower() for cmd in ["run", "execute", "start"]):
        knowledge["last_context"] = "CommandMode"
        return "CommandMode system commands available: " + ", ".join(knowledge["system_commands"])
    
    knowledge["last_context"] = "ConversationMode"
    return "ConversationMode: " + knowledge["project_knowledge"][0]
