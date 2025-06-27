"""
Mem0 Integration Module for OPRYXX
Provides contextual awareness and memory persistence using Mem0 AI
"""
import os
import json
import time
import logging
import threading
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mem0_integration")

class Mem0Client:
    """Client for interacting with Mem0 AI's API"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Mem0 client with configuration"""
        self.enabled = config.get('enabled', False)
        self.api_key = config.get('api_key', '')
        self.api_url = config.get('api_url', 'https://api.mem0.ai/v1')
        self.sync_interval = config.get('sync_interval_seconds', 60)
        self.context_window = config.get('context_window', 20)
        
        # Memory stores
        self.conversation_history: List[Dict] = []
        self.knowledge_base: Dict[str, Any] = {}
        self.last_sync = 0
        
        # Thread for background syncing
        self._sync_thread = None
        self._stop_event = threading.Event()
        
        if not self.api_key and self.enabled:
            logger.warning("Mem0 API key not provided. Mem0 integration will be disabled.")
            self.enabled = False
    
    def start(self):
        """Start the Mem0 client and background sync"""
        if not self.enabled:
            return False
            
        logger.info("Starting Mem0 client...")
        self._stop_event.clear()
        self._sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self._sync_thread.start()
        return True
    
    def stop(self):
        """Stop the Mem0 client and sync thread"""
        if not self.enabled:
            return
            
        logger.info("Stopping Mem0 client...")
        self._stop_event.set()
        if self._sync_thread and self._sync_thread.is_alive():
            self._sync_thread.join(timeout=5)
    
    def _sync_loop(self):
        """Background thread for syncing with Mem0"""
        while not self._stop_event.is_set():
            try:
                self.sync()
            except Exception as e:
                logger.error(f"Error during Mem0 sync: {e}")
            
            # Wait for sync interval or stop event
            self._stop_event.wait(self.sync_interval)
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Optional[Dict]:
        """Make an authenticated request to the Mem0 API"""
        if not self.enabled:
            return None
            
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {
            'Authorization': f"Bearer {self.api_key}",
            'Content-Type': 'application/json'
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=data)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Mem0 API request failed: {e}")
            return None
    
    def add_conversation_turn(self, role: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """Add a conversation turn to the history"""
        if not self.enabled:
            return False
            
        turn = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': metadata or {}
        }
        
        self.conversation_history.append(turn)
        
        # Keep only the most recent turns within the context window
        if len(self.conversation_history) > self.context_window:
            self.conversation_history = self.conversation_history[-self.context_window:]
        
        return True
    
    def get_context(self, max_tokens: int = 4000) -> str:
        """Get conversation context as formatted text"""
        if not self.enabled or not self.conversation_history:
            return ""
            
        # Simple implementation - just join recent messages
        context = []
        current_length = 0
        
        for turn in reversed(self.conversation_history):
            turn_text = f"{turn['role'].upper()}: {turn['content']}\n"
            if current_length + len(turn_text) > max_tokens:
                break
            context.insert(0, turn_text)
            current_length += len(turn_text)
        
        return "\n".join(context)
    
    def store_knowledge(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """Store a piece of knowledge in the knowledge base"""
        if not self.enabled:
            return False
            
        self.knowledge_base[key] = {
            'value': value,
            'metadata': metadata or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        return True
    
    def retrieve_knowledge(self, key: str) -> Optional[Any]:
        """Retrieve a piece of knowledge from the knowledge base"""
        if not self.enabled:
            return None
            
        return self.knowledge_base.get(key)
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict]:
        """Search the knowledge base for relevant information"""
        if not self.enabled:
            return []
            
        # Simple implementation - just filter by key for now
        # In a real implementation, this would use vector search or similar
        results = []
        query = query.lower()
        
        for key, value in self.knowledge_base.items():
            if query in key.lower() or query in str(value).lower():
                results.append({'key': key, 'value': value})
                if len(results) >= limit:
                    break
                    
        return results
    
    def sync(self) -> bool:
        """Sync local state with Mem0"""
        if not self.enabled:
            return False
            
        try:
            # Sync conversation history
            if self.conversation_history and len(self.conversation_history) > 0:
                response = self._make_request(
                    'conversation/history',
                    'POST',
                    {'turns': self.conversation_history}
                )
                if response and response.get('success', False):
                    self.last_sync = time.time()
            
            # Sync knowledge base
            if self.knowledge_base:
                response = self._make_request(
                    'knowledge/store',
                    'POST',
                    {'knowledge': self.knowledge_base}
                )
                if response and response.get('success', False):
                    self.last_sync = time.time()
            
            return True
            
        except Exception as e:
            logger.error(f"Error syncing with Mem0: {e}")
            return False

# Singleton instance
_mem0_instance = None

def get_mem0_client(config: Optional[Dict] = None) -> Mem0Client:
    """Get or create the Mem0 client singleton"""
    global _mem0_instance
    
    if _mem0_instance is None and config:
        _mem0_instance = Mem0Client(config)
        if _mem0_instance.enabled:
            _mem0_instance.start()
    
    return _mem0_instance

def cleanup():
    """Clean up the Mem0 client"""
    global _mem0_instance
    if _mem0_instance:
        _mem0_instance.stop()
        _mem0_instance = None

# Register cleanup on module exit
import atexit
atexit.register(cleanup)
