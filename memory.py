import sqlite3
from chromadb import Client
from sentence_transformers import SentenceTransformer
import ollama

class MemoryManager:
    def __init__(self):
        self.conn = sqlite3.connect('memory.db')
        self.conn.execute('CREATE TABLE IF NOT EXISTS session (query TEXT, response TEXT)')
        self.conn.execute('CREATE TABLE IF NOT EXISTS agent (key TEXT, value TEXT)')
        self.chroma = Client()
        self.collection = self.chroma.get_or_create_collection(name='knowledge')
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

    def add_to_session(self, query, response):
        self.conn.execute('INSERT INTO session VALUES (?, ?)', (query, response))
        self.conn.commit()

    def get_session_history(self):
        cursor = self.conn.execute('SELECT * FROM session ORDER BY rowid DESC LIMIT 5')
        return '\n'.join([f'Q: {q} A: {r}' for q, r in cursor.fetchall()])

    def update_agent_memory(self, query, response):
        prompt = f"Extract user preferences or facts from: {query} {response}"
        extracted = ollama.generate(model='llama3', prompt=prompt)['response']  # Assume dict format
        # Parse and insert; simplified
        self.conn.execute('INSERT OR REPLACE INTO agent VALUES (?, ?)', ('example_key', extracted))
        self.conn.commit()

    def retrieve_knowledge(self, query):
        embedding = self.embedder.encode([query])[0].tolist()
        results = self.collection.query(query_embeddings=[embedding], n_results=3)
        return [doc['metadata']['text'] for doc in results['documents'][0]] if results['distances'] else []

    def add_to_knowledge(self, text):
        embedding = self.embedder.encode([text])[0].tolist()
        self.collection.add(embeddings=[embedding], metadatas=[{'text': text}], ids=[str(hash(text))])