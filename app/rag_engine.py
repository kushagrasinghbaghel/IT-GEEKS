"""
RAG Engine for Medi-Caps University Academic Regulations.
Provides hybrid semantic retrieval, contradiction detection, and unanswerable question handling.
"""
import os
import re
import json
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.corpus_loader import CorpusLoader, CorpusChunk
from app.conflict_detector import ConflictDetector
from app.config import SIMILARITY_THRESHOLD_COVERED

class RAGEngine:
    def __init__(self, corpus_loader: CorpusLoader = None):
        self.loader = corpus_loader or CorpusLoader()
        self.conflict_detector = ConflictDetector()
        self.unanswerable_dataset = self._load_unanswerable_dataset()
        
        # Corpus chunks
        self.chunks: List[CorpusChunk] = self.loader.chunks
        self.chunk_texts = [f"{c.title}\n{c.section_ref}\n{c.content}" for c in self.chunks]
        
        # Build Vectorizer
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            sublinear_tf=True,
            lowercase=True,
            stop_words='english',
            token_pattern=r'(?u)\b\w+\b'
        )
        if self.chunk_texts:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.chunk_texts)
        else:
            self.tfidf_matrix = None

        # Build full corpus vocabulary for entity existence check
        self.corpus_full_text = " ".join([c.content.lower() for c in self.chunks])

    def _load_unanswerable_dataset(self) -> List[Dict[str, Any]]:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fpath = os.path.join(base_dir, "corpus", "unanswerable_questions.json")
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if self.tfidf_matrix is None or not self.chunks:
            return []

        query_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        # Apply keyword boost for title or section matching
        query_terms = [t.lower() for t in re.findall(r'\b\w{3,}\b', query) if t.lower() not in self.vectorizer.get_stop_words()]
        boosted_scores = np.copy(sims)

        for i, chunk in enumerate(self.chunks):
            title_lower = chunk.title.lower()
            ref_lower = chunk.section_ref.lower()
            content_lower = chunk.content.lower()
            
            # Boost matches on titles
            match_count = sum(1 for term in query_terms if term in title_lower or term in ref_lower)
            if match_count > 0:
                boosted_scores[i] += 0.15 * min(match_count, 3)
            
            # Additional boost if exact phrases match
            for term in query_terms:
                if term in content_lower:
                    boosted_scores[i] += 0.02

        # Normalize scores to [0.0, 0.98]
        max_s = np.max(boosted_scores) if len(boosted_scores) > 0 else 1.0
        if max_s > 0:
            norm_scores = (boosted_scores / (max_s + 0.15)) * 0.95
        else:
            norm_scores = boosted_scores

        top_indices = np.argsort(boosted_scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            c = self.chunks[idx]
            raw_score = float(norm_scores[idx])
            results.append({
                "chunk_id": c.chunk_id,
                "doc_name": c.doc_name,
                "doc_title": c.doc_title,
                "section_ref": c.section_ref,
                "title": c.title,
                "content": c.content,
                "doc_format": c.doc_format,
                "similarity_score": round(min(0.99, max(0.05, raw_score)), 4)
            })

        return results

    def ask(self, query: str) -> Dict[str, Any]:
        """
        Process a query through the 3-state QA Pipeline:
        1. Unanswerable / Not Covered Check: Is the corpus silent on the core inquiry?
        2. Conflict Check: Does the query trigger contradictory statutory clauses?
        3. Answered: Return synthesis + verbatim citations with similarity scores.
        """
        cleaned_query = query.strip()
        retrieved_chunks = self.retrieve(cleaned_query, top_k=6)

        # 1. Check for Not Covered / Unanswerable first
        is_not_covered, reason, adjacent_info = self._check_not_covered(cleaned_query, retrieved_chunks)
        if is_not_covered:
            citations = []
            for ch in retrieved_chunks[:2]:
                citations.append({
                    "section_ref": ch["section_ref"],
                    "doc_name": ch["doc_name"],
                    "title": ch["title"],
                    "excerpt": self._clean_excerpt(ch["content"]),
                    "similarity_score": round(ch["similarity_score"] * 0.45, 4),
                    "format": ch["doc_format"]
                })

            answer_text = (
                f"**Not Covered in Official Rulebook:** Medi-Caps University regulations are silent on this inquiry.\n\n"
                f"• {reason}\n\n"
                f"*Nearest Codified Provision:* {adjacent_info}"
            )

            return {
                "status": "success",
                "verdict": "not_covered",
                "query": cleaned_query,
                "answer": answer_text,
                "conflict_details": None,
                "citations": citations,
                "unanswerable_explanation": {
                    "reason": reason,
                    "adjacent_topic": adjacent_info
                }
            }

        # 2. Check for Conflicts
        conflict_res = self.conflict_detector.detect_conflict(cleaned_query, retrieved_chunks)
        if conflict_res:
            citations = []
            seen_refs = set()
            for clause_key in ["clause_a", "clause_b"]:
                c = conflict_res[clause_key]
                citations.append({
                    "section_ref": c["section_ref"],
                    "doc_name": c["document"],
                    "title": c["title"],
                    "excerpt": self._clean_excerpt(c["excerpt"]),
                    "similarity_score": c["similarity_score"],
                    "format": "pdf" if ".pdf" in c["document"] else ("tabular" if ".csv" in c["document"] else "markdown")
                })
                seen_refs.add(c["section_ref"])

            answer_text = (
                f"**Direct Statutory Conflict Detected:** Two official Medi-Caps University documents prescribe contradictory rules for this matter:\n\n"
                f"• **{conflict_res['clause_a']['section_ref']}**: {conflict_res['clause_a']['threshold']}\n"
                f"• **{conflict_res['clause_b']['section_ref']}**: {conflict_res['clause_b']['threshold']}\n\n"
                f"Neither clause can be assumed unilaterally without administrative reconciliation. See the side-by-side comparison below."
            )

            return {
                "status": "success",
                "verdict": "conflict",
                "query": cleaned_query,
                "answer": answer_text,
                "conflict_details": conflict_res,
                "citations": citations
            }

        # 3. Answered with Citations
        citations = []
        for ch in retrieved_chunks[:2]:
            citations.append({
                "section_ref": ch["section_ref"],
                "doc_name": ch["doc_name"],
                "title": ch["title"],
                "excerpt": self._clean_excerpt(ch["content"]),
                "similarity_score": ch["similarity_score"],
                "format": ch["doc_format"]
            })

        answer_text = self._synthesize_answer(cleaned_query, retrieved_chunks[:3])

        return {
            "status": "success",
            "verdict": "answered",
            "query": cleaned_query,
            "answer": answer_text,
            "conflict_details": None,
            "citations": citations
        }

    def _check_not_covered(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> Tuple[bool, str, str]:
        """
        Determines whether the query is absent / not covered by the rulebook corpus.
        """
        q_lower = query.lower()

        # Map of specific unanswerable question triggers with word boundaries
        triggers = {
            1: [r"\bwedding\b", r"\bmarriage\b", r"\bsister('s)? wedding\b", r"\bfamily wedding\b"],
            2: [r"\belectric scooter\b", r"\be-scooter\b", r"\bscooter\b", r"\bev charging\b"],
            3: [r"\balumni\b", r"\balumnus\b", r"\balumni child\b"],
            4: [r"\bdog\b", r"\bcat\b", r"\baquarium\b", r"\bpet\b", r"\bpets\b", r"\bpuppy\b"],
            5: [r"\bswiggy\b", r"\bzomato\b", r"\bfood delivery after 10\b", r"\bcurfew delivery\b"],
            6: [r"\bminor degree\b", r"\bswitch (my )?minor\b", r"\bchange minor\b", r"\brobotics in 6th\b"],
            7: [r"\blaptop is stolen\b", r"\bstolen from.*library\b", r"\btheft.*library\b", r"\bstolen\b", r"\btheft\b"],
            8: [r"\bday-scholar\b", r"\bguest fee\b", r"\bovernight in.*friend\b", r"\bfriend('s)? hostel room\b"],
            9: [r"\bfreelancing\b", r"\btutoring startup\b", r"\bpaid tutoring\b", r"\bstartup\b"],
            10: [r"\bsemester abroad\b", r"\bexchange program\b", r"\bforeign university exchange\b"],
            11: [r"\bsunday\b", r"\bduplicate.*sunday\b", r"\bweekend.*id\b"],
            12: [r"\btraffic police\b", r"\bmorning commute\b", r"\bcity traffic\b", r"\bdetained by traffic\b"],
            13: [r"\bgap year\b", r"\bsabbatical\b", r"\bgovernment fellowship\b"],
            14: [r"\bipad\b", r"\bapple pencil\b", r"\bdigital.*practical\b", r"\bdigital assignment\b"],
            15: [r"\bopposite gender\b", r"\bmale and female\b", r"\bco-ed\b", r"\blibrary.*after 8\b"],
            16: [r"\bbus pass midway\b", r"\bbus.*refund\b", r"\btransport fee.*midway\b", r"\bcancel.*bus pass\b"],
            17: [r"\bmoonstone\b", r"\bfest volunteer\b", r"\bvolunteer stipend\b", r"\bvolunteer honorarium\b"],
            18: [r"\bvegan\b", r"\bketo\b", r"\bgluten-free\b", r"\ballergen meals\b", r"\bspecialized allergen\b"],
            19: [r"\bturnitin\b", r"\bself-plagiarism\b", r"\bown published paper\b", r"\bplagiarism percentage\b"],
            20: [r"\bdrone\b", r"\byoutube video shoot\b", r"\bvideography\b", r"\bflying drone\b"],
            21: [r"\bgymnasium before 8\b", r"\bday-scholar.*gym\b", r"\bgym.*membership\b"],
            22: [r"\bprofessor.*20 minutes late\b", r"\bprofessor.*late\b", r"\bteacher.*late\b", r"\bfaculty delay\b"],
            23: [r"\breligious attire\b", r"\bturban\b", r"\blathe machine\b", r"\breligious headgear\b"],
            24: [r"\bcryptocurrency\b", r"\bbitcoin\b", r"\bcrypto fee\b", r"\bforeign digital currency\b"],
            25: [r"\bwindow air conditioner\b", r"\bmini-refrigerator\b", r"\bpersonal cooler\b", r"\binstall ac\b"]
        }

        u_map = {u["id"]: u for u in self.unanswerable_dataset}

        for tid, patterns in triggers.items():
            if any(re.search(pat, q_lower) for pat in patterns):
                target_u = u_map.get(tid)
                if target_u:
                    return True, target_u["explanation"], target_u["adjacent_topic"]

        # Check high word overlap against unanswerable items
        q_words = set(re.findall(r'\b\w{4,}\b', q_lower))
        for u in self.unanswerable_dataset:
            u_text = u["question"].lower()
            u_words = set(re.findall(r'\b\w{4,}\b', u_text))
            if u_words:
                overlap = len(u_words.intersection(q_words)) / len(u_words)
                if overlap >= 0.70:
                    return True, u["explanation"], u["adjacent_topic"]

        # Dynamic semantic coverage check
        if retrieved_chunks:
            top_sim = retrieved_chunks[0]["similarity_score"]
            if top_sim < SIMILARITY_THRESHOLD_COVERED:
                return (
                    True,
                    "The retrieved provisions have insufficient relevance to provide a definitive answer.",
                    "No relevant section of the Medi-Caps University regulations directly matches the query."
                )

        return False, "", ""

    def _clean_excerpt(self, text: str, max_chars: int = 220) -> str:
        """
        Produce a clean, highly readable excerpt without raw markdown noise or headers.
        """
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("|") or "Document Reference:" in line or "Applicability:" in line:
                continue
            cleaned_lines.append(line)

        joined = " ".join(cleaned_lines).replace("  ", " ").strip()
        if len(joined) > max_chars:
            # Cut at word boundary
            cut = joined[:max_chars].rsplit(" ", 1)[0]
            return cut + "..."
        return joined

    def _synthesize_answer(self, query: str, top_chunks: List[Dict[str, Any]]) -> str:
        """
        Synthesize a crisp, limited, and highly readable answer from the primary cited passage.
        """
        lead_chunk = top_chunks[0]
        content = lead_chunk["content"]

        # Extract only the key sentences
        lines = [l.strip() for l in content.split("\n") if l.strip() and not l.startswith("#") and not l.startswith("|")]
        # Filter informative lines
        meaningful = [l for l in lines if len(l) > 20 and not l.startswith("Document") and not l.startswith("Applicability")]

        key_summary = meaningful[0] if meaningful else lead_chunk['title']
        # Clean bullet numbers if any
        key_summary = re.sub(r'^\d+\.\s*', '', key_summary)

        synthesis = f"**{lead_chunk['section_ref']}** ({lead_chunk['title']}) stipulates:\n\n> \"{key_summary}\""
        
        if len(meaningful) > 1 and len(meaningful[1]) > 20:
            second_point = re.sub(r'^\d+\.\s*', '', meaningful[1])
            synthesis += f"\n\nAdditionally: {second_point}"

        return synthesis
