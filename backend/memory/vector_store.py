import chromadb
import hashlib
import json
import os
from typing import List, Dict

class ChromaVectorStore:
    def __init__(self, persist_dir: str = None):
        if persist_dir is None:
            persist_dir = os.path.join(os.path.dirname(__file__), "..", "data", "chroma_store")
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name="incidents", metadata={"hnsw:space": "cosine"})

    def _generate_id(self, event: Dict) -> str:
        content = json.dumps(event, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def add_incident(self, incident: Dict) -> str:
        incident_id = self._generate_id(incident)
        summary = f"""Event: {incident.get('trigger_event', 'Unknown')}
MITRE Technique: {incident.get('mitre_technique', 'Unknown')}
Attack Chain: {incident.get('attack_chain', 'Unknown')}
Risk Score: {incident.get('risk_score', 0)}
Response: {incident.get('response_taken', 'Unknown')}"""

        self.collection.add(documents=[summary], metadatas=[{"id": incident_id, "trigger_event": incident.get("trigger_event", ""), "mitre_technique": incident.get("mitre_technique", ""), "risk_score": str(incident.get("risk_score", 0)), "response_taken": incident.get("response_taken", "")}], ids=[incident_id])
        return incident_id

    def query_similar_incidents(self, query_event: Dict, top_k: int = 3) -> List[Dict]:
        query_text = f"Event: {query_event.get('details', {}).get('location', 'Unknown')} User: {query_event.get('user', 'Unknown')} Type: {query_event.get('type', 'Unknown')}"
        try:
            count = self.collection.count()
            if count == 0:
                return []
            results = self.collection.query(query_texts=[query_text], n_results=min(top_k, count))
            incidents = []
            if results and results.get("metadatas"):
                for i, metadata in enumerate(results["metadatas"][0]):
                    incidents.append({"id": metadata.get("id", f"unknown_{i}"), "summary": "Similar incident from past memory", "mitre_technique": metadata.get("mitre_technique", ""), "response_taken": metadata.get("response_taken", "")})
            return incidents
        except Exception as e:
            print(f"Vector store query error: {e}")
            return []

    def get_incident_count(self) -> int:
        return self.collection.count()

    def reset(self):
        self.client.delete_collection("incidents")
        self.collection = self.client.get_or_create_collection(name="incidents", metadata={"hnsw:space": "cosine"})

vector_store = ChromaVectorStore()

def query_similar_incidents(event: Dict, top_k: int = 3) -> List[Dict]:
    return vector_store.query_similar_incidents(event, top_k)

def add_incident_to_memory(incident: Dict) -> str:
    return vector_store.add_incident(incident)
