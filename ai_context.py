from sentence_transformers import SentenceTransformer
import pickle
import os
import json
from datetime import datetime

CONTEXT_FILE = "ai_context.pkl"
CHAT_LOG_DIR = "chat_logs"

def initialize():
    """Initialize the AI context with default knowledge"""
    try:
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
            print("AI context initialized successfully")
        else:
            print("AI context already exists")
    except Exception as e:
        print(f"Error initializing AI context: {e}")

def get_context(query):
    """Retrieve and update context for a query"""
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Load existing knowledge
        with open(CONTEXT_FILE, "rb") as f:
            knowledge = pickle.load(f)

        # Update conversation history
        knowledge["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "context": knowledge["last_context"]
        })

        # Enhanced context matching
        context_response = ""
        if any(cmd in query.lower() for cmd in ["run", "execute", "start"]):
            knowledge["last_context"] = "CommandMode"
            context_response = "CommandMode system commands available: " + ", ".join(knowledge["system_commands"])
        else:
            knowledge["last_context"] = "ConversationMode"
            context_response = "ConversationMode: " + knowledge["project_knowledge"][0]

        # Save updated knowledge back to file
        with open(CONTEXT_FILE, "wb") as f:
            pickle.dump(knowledge, f)

        # Save chat log
        save_chat_log(query, context_response)

        return context_response

    except FileNotFoundError:
        print("Context file not found. Please run initialize() first.")
        return "Error: Context not initialized"
    except Exception as e:
        print(f"Error retrieving context: {e}")
        return f"Error: {e}"

def save_chat_log(query, response):
    """Save chat interaction to log file"""
    try:
        timestamp = datetime.now()
        log_filename = f"chat_{timestamp.strftime('%Y%m%d')}.json"
        log_path = os.path.join(CHAT_LOG_DIR, log_filename)

        chat_entry = {
            "timestamp": timestamp.isoformat(),
            "query": query,
            "response": response
        }

        # Load existing log or create new one
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                chat_log = json.load(f)
        else:
            chat_log = []

        chat_log.append(chat_entry)

        # Save updated log
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(chat_log, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"Error saving chat log: {e}")

def get_conversation_history(limit=10):
    """Get recent conversation history"""
    try:
        with open(CONTEXT_FILE, "rb") as f:
            knowledge = pickle.load(f)
        return knowledge["conversation_history"][-limit:]
    except Exception as e:
        print(f"Error retrieving conversation history: {e}")
        return []

def update_project_knowledge(new_knowledge):
    """Add new knowledge to the project knowledge base"""
    try:
        with open(CONTEXT_FILE, "rb") as f:
            knowledge = pickle.load(f)

        if new_knowledge not in knowledge["project_knowledge"]:
            knowledge["project_knowledge"].append(new_knowledge)

            with open(CONTEXT_FILE, "wb") as f:
                pickle.dump(knowledge, f)
            print(f"Added new knowledge: {new_knowledge}")
        else:
            print("Knowledge already exists")

    except Exception as e:
        print(f"Error updating project knowledge: {e}")

def clear_context():
    """Clear all context data"""
    try:
        if os.path.exists(CONTEXT_FILE):
            os.remove(CONTEXT_FILE)
        print("Context cleared successfully")
    except Exception as e:
        print(f"Error clearing context: {e}")

# Initialize on import
if __name__ == "__main__":
    initialize()
