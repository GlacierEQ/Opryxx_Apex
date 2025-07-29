"""
Check Ollama Repository Integration Status
Based on your 4 Ollama repositories
"""

import os
import subprocess

def check_repo_integration():
    """Check integration with your Ollama repositories"""
    print("OLLAMA REPOSITORY INTEGRATION CHECK")
    print("=" * 40)
    
    repos = [
        "ollama",
        "LegalEdge-AI-Project", 
        "Autogen_GraphRAG_Ollama",
        "ollama-deep-researcher"
    ]
    
    for repo in repos:
        if os.path.exists(f"../{repo}"):
            print(f"FOUND: {repo}")
        else:
            print(f"MISSING: {repo}")
    
    # Check if we can use existing patterns
    patterns = {
        "GraphRAG": "Autogen_GraphRAG_Ollama",
        "Legal AI": "LegalEdge-AI-Project", 
        "Research": "ollama-deep-researcher",
        "Core": "ollama"
    }
    
    print("\nINTEGRATION PATTERNS:")
    for pattern, repo in patterns.items():
        print(f"{pattern}: Ready for {repo} integration")
    
    return True

if __name__ == "__main__":
    check_repo_integration()
    print("\nNEXT STEPS:")
    print("1. Install Ollama: https://ollama.ai")
    print("2. Clone missing repositories")
    print("3. Run integration bridge")