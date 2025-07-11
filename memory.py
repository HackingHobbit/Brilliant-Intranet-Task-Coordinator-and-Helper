import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import os

# Import for vector embeddings
try:
    from chromadb import Client, Collection
    from sentence_transformers import SentenceTransformer
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logging.warning("ChromaDB not available. Knowledge base features will be disabled.")

# Import for token counting
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logging.warning("tiktoken not available. Using character-based token estimation.")

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages session memory, agent memory, and knowledge base"""
    
    def __init__(self, db_path: str = "memory.db", max_session_history: int = 50):
        """
        Initialize memory manager
        
        Args:
            db_path: Path to SQLite database
            max_session_history: Maximum number of session entries to keep
        """
        self.db_path = db_path
        self.max_session_history = max_session_history
        
        # Initialize SQLite database
        self._init_database()
        
        # Initialize ChromaDB for knowledge base
        if CHROMA_AVAILABLE:
            self._init_chroma()
        else:
            self.chroma_client = None
            self.knowledge_collection = None
            self.embedder = None

        # Initialize token encoder
        if TIKTOKEN_AVAILABLE:
            try:
                self.token_encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
            except Exception as e:
                logger.warning(f"Failed to initialize tiktoken: {e}")
                self.token_encoder = None
        else:
            self.token_encoder = None
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable dict-like access
            
            # Create tables
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS session_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    metadata TEXT
                )
            ''')
            
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS agent_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT NOT NULL,
                    category TEXT DEFAULT 'preference',
                    metadata TEXT
                )
            ''')
            
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    content TEXT NOT NULL,
                    source TEXT,
                    category TEXT,
                    metadata TEXT
                )
            ''')
            
            # Create indexes for better performance
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_session_timestamp ON session_memory(timestamp)')
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_agent_key ON agent_memory(key)')
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_base(category)')
            
            self.conn.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _init_chroma(self):
        """Initialize ChromaDB for vector embeddings"""
        try:
            self.chroma_client = Client()
            self.knowledge_collection = self.chroma_client.get_or_create_collection(
                name="knowledge_base",
                metadata={"description": "AI Avatar Knowledge Base"}
            )
            
            # Initialize sentence transformer for embeddings
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("ChromaDB initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.chroma_client = None
            self.knowledge_collection = None
            self.embedder = None
    
    def add_to_session(self, query: str, response: str, metadata: Optional[Dict] = None):
        """
        Add a conversation turn to session memory
        
        Args:
            query: User query
            response: AI response
            metadata: Optional metadata
        """
        try:
            metadata_json = json.dumps(metadata) if metadata else None
            
            self.conn.execute('''
                INSERT INTO session_memory (query, response, metadata)
                VALUES (?, ?, ?)
            ''', (query, response, metadata_json))
            
            # Clean up old entries if we exceed max_history
            self._cleanup_session_history()
            
            self.conn.commit()
            logger.debug(f"Added to session memory: {query[:50]}...")
            
        except Exception as e:
            logger.error(f"Failed to add to session memory: {e}")
            raise
    
    def get_session_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get recent session history
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of session entries
        """
        try:
            if limit is None:
                limit = self.max_session_history
            
            cursor = self.conn.execute('''
                SELECT query, response, timestamp, metadata
                FROM session_memory
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            history = []
            for row in cursor.fetchall():
                entry = {
                    'query': row['query'],
                    'response': row['response'],
                    'timestamp': row['timestamp'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None
                }
                history.append(entry)
            
            # Return in chronological order
            history.reverse()
            return history
            
        except Exception as e:
            logger.error(f"Failed to get session history: {e}")
            return []
    
    def get_session_context(self, max_tokens: int = 1000) -> str:
        """
        Get session history as context string for LLM

        Args:
            max_tokens: Approximate maximum tokens for context

        Returns:
            Formatted context string
        """
        try:
            history = self.get_session_history()

            context_parts = []
            current_tokens = 0

            for entry in history:
                turn = f"User: {entry['query']}\nAssistant: {entry['response']}\n"
                turn_tokens = self.count_tokens(turn)

                if current_tokens + turn_tokens > max_tokens:
                    break

                context_parts.append(turn)
                current_tokens += turn_tokens

            return "\n".join(context_parts)

        except Exception as e:
            logger.error(f"Failed to get session context: {e}")
            return ""

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        try:
            if self.token_encoder:
                return len(self.token_encoder.encode(text))
            else:
                # Fallback: rough estimation (4 characters per token)
                return len(text) // 4
        except Exception as e:
            logger.error(f"Token counting failed: {e}")
            return len(text) // 4
    
    def update_agent_memory(self, query: str, response: str):
        """
        Update agent memory with extracted preferences/facts
        
        Args:
            query: User query
            response: AI response
        """
        try:
            # Simple extraction of potential preferences
            # In a real implementation, you might use an LLM to extract this
            text = f"{query} {response}".lower()
            
            # Extract basic preferences
            preferences = {}
            
            if "email" in text and "gmail" in text:
                preferences["email_provider"] = "gmail"
            elif "email" in text and "outlook" in text:
                preferences["email_provider"] = "outlook"
            elif "email" in text and "icloud" in text:
                preferences["email_provider"] = "icloud"
            
            if "calendar" in text:
                preferences["calendar_enabled"] = True
            
            if "finance" in text or "stock" in text:
                preferences["financial_queries"] = True
            
            # Store preferences
            for key, value in preferences.items():
                self.conn.execute('''
                    INSERT OR REPLACE INTO agent_memory (key, value, category)
                    VALUES (?, ?, ?)
                ''', (key, str(value), 'preference'))
            
            self.conn.commit()
            logger.debug(f"Updated agent memory with {len(preferences)} preferences")
            
        except Exception as e:
            logger.error(f"Failed to update agent memory: {e}")
    
    def get_agent_memory(self, category: Optional[str] = None) -> Dict[str, str]:
        """
        Get agent memory entries
        
        Args:
            category: Optional category filter
            
        Returns:
            Dictionary of memory entries
        """
        try:
            if category:
                cursor = self.conn.execute('''
                    SELECT key, value, category, metadata
                    FROM agent_memory
                    WHERE category = ?
                    ORDER BY timestamp DESC
                ''', (category,))
            else:
                cursor = self.conn.execute('''
                    SELECT key, value, category, metadata
                    FROM agent_memory
                    ORDER BY timestamp DESC
                ''')
            
            memory = {}
            for row in cursor.fetchall():
                memory[row['key']] = {
                    'value': row['value'],
                    'category': row['category'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None
                }
            
            return memory
            
        except Exception as e:
            logger.error(f"Failed to get agent memory: {e}")
            return {}
    
    def add_to_knowledge_base(self, content: str, source: Optional[str] = None, 
                             category: Optional[str] = None, metadata: Optional[Dict] = None):
        """
        Add content to knowledge base
        
        Args:
            content: Content to store
            source: Source of the content
            category: Category for organization
            metadata: Additional metadata
        """
        try:
            # Store in SQLite
            metadata_json = json.dumps(metadata) if metadata else None
            
            self.conn.execute('''
                INSERT INTO knowledge_base (content, source, category, metadata)
                VALUES (?, ?, ?, ?)
            ''', (content, source, category, metadata_json))
            
            # Store in ChromaDB if available
            if self.knowledge_collection and self.embedder:
                embedding = self.embedder.encode(content).tolist()
                self.knowledge_collection.add(
                    embeddings=[embedding],
                    documents=[content],
                    metadatas=[{
                        'source': source or 'unknown',
                        'category': category or 'general',
                        'timestamp': datetime.now().isoformat()
                    }]
                )
            
            self.conn.commit()
            logger.debug(f"Added to knowledge base: {content[:50]}...")
            
        except Exception as e:
            logger.error(f"Failed to add to knowledge base: {e}")
            raise
    
    def retrieve_knowledge(self, query: str, limit: int = 5) -> str:
        """
        Retrieve relevant knowledge for a query
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Retrieved knowledge as string
        """
        try:
            if not self.knowledge_collection or not self.embedder:
                # Fallback to SQLite search
                cursor = self.conn.execute('''
                    SELECT content FROM knowledge_base
                    WHERE content LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (f'%{query}%', limit))
                
                results = [row['content'] for row in cursor.fetchall()]
                return " ".join(results)
            
            # Use ChromaDB for semantic search
            query_embedding = self.embedder.encode(query).tolist()
            
            results = self.knowledge_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            
            if results['documents']:
                return " ".join(results['documents'][0])
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Failed to retrieve knowledge: {e}")
            return ""
    
    def clear_session(self):
        """Clear all session memory"""
        try:
            self.conn.execute('DELETE FROM session_memory')
            self.conn.commit()
            logger.info("Session memory cleared")
        except Exception as e:
            logger.error(f"Failed to clear session memory: {e}")
    
    def clear_agent_memory(self):
        """Clear all agent memory"""
        try:
            self.conn.execute('DELETE FROM agent_memory')
            self.conn.commit()
            logger.info("Agent memory cleared")
        except Exception as e:
            logger.error(f"Failed to clear agent memory: {e}")
    
    def clear_knowledge_base(self):
        """Clear all knowledge base entries"""
        try:
            self.conn.execute('DELETE FROM knowledge_base')
            self.conn.commit()
            
            if self.knowledge_collection:
                self.knowledge_collection.delete(where={})
            
            logger.info("Knowledge base cleared")
        except Exception as e:
            logger.error(f"Failed to clear knowledge base: {e}")
    
    def _cleanup_session_history(self):
        """Remove old session entries if we exceed max_history"""
        try:
            cursor = self.conn.execute('SELECT COUNT(*) FROM session_memory')
            count = cursor.fetchone()[0]
            
            if count > self.max_session_history:
                # Delete oldest entries
                self.conn.execute('''
                    DELETE FROM session_memory
                    WHERE id IN (
                        SELECT id FROM session_memory
                        ORDER BY timestamp ASC
                        LIMIT ?
                    )
                ''', (count - self.max_session_history,))
                
                self.conn.commit()
                logger.debug(f"Cleaned up {count - self.max_session_history} old session entries")
                
        except Exception as e:
            logger.error(f"Failed to cleanup session history: {e}")
    
    def get_memory_stats(self) -> Dict:
        """Get memory statistics"""
        try:
            stats = {}
            
            # Session memory stats
            cursor = self.conn.execute('SELECT COUNT(*) FROM session_memory')
            stats['session_entries'] = cursor.fetchone()[0]
            
            # Agent memory stats
            cursor = self.conn.execute('SELECT COUNT(*) FROM agent_memory')
            stats['agent_entries'] = cursor.fetchone()[0]
            
            # Knowledge base stats
            cursor = self.conn.execute('SELECT COUNT(*) FROM knowledge_base')
            stats['knowledge_entries'] = cursor.fetchone()[0]
            
            # ChromaDB stats
            if self.knowledge_collection:
                stats['chroma_available'] = True
                stats['chroma_count'] = self.knowledge_collection.count()
            else:
                stats['chroma_available'] = False
                stats['chroma_count'] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    # Test memory manager
    memory = MemoryManager()
    
    # Test session memory
    memory.add_to_session("Hello", "Hi there!")
    memory.add_to_session("How are you?", "I'm doing well, thank you!")
    
    history = memory.get_session_history()
    print(f"Session history: {len(history)} entries")
    
    # Test agent memory
    memory.update_agent_memory("I use Gmail for email", "I'll remember that")
    agent_memory = memory.get_agent_memory()
    print(f"Agent memory: {len(agent_memory)} entries")
    
    # Test knowledge base
    memory.add_to_knowledge_base("The capital of France is Paris", source="user", category="geography")
    knowledge = memory.retrieve_knowledge("France")
    print(f"Retrieved knowledge: {knowledge}")
    
    # Print stats
    stats = memory.get_memory_stats()
    print(f"Memory stats: {stats}")
    
    memory.close() 