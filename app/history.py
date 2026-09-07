"""
Query History & Audit Log Manager for Medi-Caps Regulations QA.
Stores query sessions, verdict classifications, citations, and latencies.
"""
import os
import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "corpus", "query_history.json")

class HistoryManager:
    def __init__(self, history_file: str = HISTORY_FILE):
        self.history_file = history_file
        self.records: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.records = json.load(f)
            except Exception:
                self.records = []
        else:
            self.records = []

    def _save(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=2)
        except Exception:
            pass

    def add_entry(
        self,
        query: str,
        verdict: str,
        answer: str,
        citations: List[Dict[str, Any]],
        latency_ms: float,
        user_email: str = "guest@medicaps.ac.in",
        conflict_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        entry = {
            "id": f"rec_{int(time.time()*1000)}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "epoch": time.time(),
            "user_email": user_email,
            "query": query,
            "verdict": verdict,
            "answer_preview": answer[:220] + ("..." if len(answer) > 220 else ""),
            "full_answer": answer,
            "latency_ms": round(latency_ms, 2),
            "citations_count": len(citations),
            "citations_summary": [c.get("section_ref", "") for c in citations[:4]],
            "conflict_detected": conflict_details is not None,
            "conflict_title": conflict_details.get("title") if conflict_details else None
        }
        self.records.insert(0, entry) # Most recent first
        # Keep maximum 200 records
        if len(self.records) > 200:
            self.records = self.records[:200]
        self._save()
        return entry

    def get_entries(
        self,
        verdict: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        results = self.records
        if verdict and verdict != "all":
            results = [r for r in results if r["verdict"] == verdict]
        if search:
            s_lower = search.lower()
            results = [r for r in results if s_lower in r["query"].lower() or s_lower in r["answer_preview"].lower()]
        return results[:limit]

    def clear(self):
        self.records = []
        self._save()
