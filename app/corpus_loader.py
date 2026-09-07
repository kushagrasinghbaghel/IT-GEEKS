"""
Corpus Loader for Medi-Caps University Academic Regulations.
Loads and chunks Markdown documents, Tabular CSV/Markdown files, and PDFs.
"""
import os
import re
import csv
from typing import List, Dict, Any
from pypdf import PdfReader
from app.config import CORPUS_DIR

class CorpusChunk:
    def __init__(
        self,
        chunk_id: str,
        doc_name: str,
        doc_title: str,
        section_ref: str,
        title: str,
        content: str,
        doc_format: str,
        extra_metadata: Dict[str, Any] = None
    ):
        self.chunk_id = chunk_id
        self.doc_name = doc_name
        self.doc_title = doc_title
        self.section_ref = section_ref
        self.title = title
        self.content = content.strip()
        self.doc_format = doc_format
        self.word_count = len(self.content.split())
        self.extra_metadata = extra_metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_name": self.doc_name,
            "doc_title": self.doc_title,
            "section_ref": self.section_ref,
            "title": self.title,
            "content": self.content,
            "doc_format": self.doc_format,
            "word_count": self.word_count,
            "extra_metadata": self.extra_metadata
        }


class CorpusLoader:
    def __init__(self, corpus_dir: str = CORPUS_DIR):
        self.corpus_dir = corpus_dir
        self.chunks: List[CorpusChunk] = []
        self.doc_stats: Dict[str, Dict[str, Any]] = {}
        self.total_word_count = 0
        self.load_all()

    def load_all(self):
        self.chunks = []
        self.doc_stats = {}
        self.total_word_count = 0

        if not os.path.exists(self.corpus_dir):
            return

        for filename in sorted(os.listdir(self.corpus_dir)):
            filepath = os.path.join(self.corpus_dir, filename)
            if filename.endswith(".md"):
                self._load_markdown(filename, filepath)
            elif filename.endswith(".csv"):
                self._load_csv(filename, filepath)
            elif filename.endswith(".pdf"):
                self._load_pdf(filename, filepath)

    def _load_markdown(self, filename: str, filepath: str):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        words = len(text.split())
        self.total_word_count += words
        self.doc_stats[filename] = {
            "name": filename,
            "format": "markdown",
            "word_count": words,
            "chunks_count": 0
        }

        # Extract title from first H1/H2
        doc_title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        doc_title = doc_title_match.group(1).strip() if doc_title_match else filename

        # Split markdown by sections (#### § or ### SECTION)
        # Using regex split to retain delimiter information
        pattern = r"(?=####\s+§\s*[\d\.]+)"
        raw_chunks = re.split(pattern, text)

        chunk_idx = 0
        for raw in raw_chunks:
            raw = raw.strip()
            if not raw:
                continue

            # Check if this chunk has a section header
            section_match = re.search(r"####\s+(§\s*[\d\.]+)\s*([^\n\r]+)", raw)
            if section_match:
                section_num = section_match.group(1).strip()
                clause_title = section_match.group(2).strip()
                section_ref = f"{self._clean_doc_name(filename)} {section_num}"
                full_title = f"{section_num} {clause_title}"
            else:
                # Top-level preamble or section header
                sec_header_match = re.search(r"###\s+SECTION\s*[\d]+[:\s]*([^\n\r]+)", raw)
                if sec_header_match:
                    section_ref = f"{self._clean_doc_name(filename)} Section Overview"
                    full_title = sec_header_match.group(1).strip()
                else:
                    section_ref = f"{self._clean_doc_name(filename)} Preamble"
                    full_title = "General Provisions"

            chunk_id = f"{filename}_{chunk_idx}"
            chunk = CorpusChunk(
                chunk_id=chunk_id,
                doc_name=filename,
                doc_title=doc_title,
                section_ref=section_ref,
                title=full_title,
                content=raw,
                doc_format="markdown"
            )
            self.chunks.append(chunk)
            chunk_idx += 1

        self.doc_stats[filename]["chunks_count"] = chunk_idx

    def _load_csv(self, filename: str, filepath: str):
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()

        words = len(raw_text.split())
        self.total_word_count += words
        self.doc_stats[filename] = {
            "name": filename,
            "format": "tabular_csv",
            "word_count": words,
            "chunks_count": 0
        }

        # Group rows by category
        categories: Dict[str, List[Dict[str, str]]] = {}
        for row in rows:
            cat = row.get("category", "General")
            categories.setdefault(cat, []).append(row)

        chunk_idx = 0
        for cat, cat_rows in categories.items():
            content_lines = [f"### Category: {cat.upper()} FEE AND DEADLINE SCHEDULE"]
            for r in cat_rows:
                content_lines.append(
                    f"- Item: {r.get('service_item')} | Standard Fee: Rs. {r.get('standard_fee_inr')} | "
                    f"Late Fine: Rs. {r.get('late_surcharge_inr')} | Conditions: {r.get('conditions_and_deadlines')}"
                )
            content = "\n".join(content_lines)
            chunk = CorpusChunk(
                chunk_id=f"{filename}_{chunk_idx}",
                doc_name=filename,
                doc_title="Medi-Caps Comprehensive Fee Deadlines Schedule (Tabular)",
                section_ref=f"Fee Schedule Tabular § {cat.capitalize()}",
                title=f"{cat.capitalize()} Fee & Deadline Tariffs",
                content=content,
                doc_format="tabular"
            )
            self.chunks.append(chunk)
            chunk_idx += 1

        self.doc_stats[filename]["chunks_count"] = chunk_idx

    def _load_pdf(self, filename: str, filepath: str):
        reader = PdfReader(filepath)
        full_text = ""
        for page in reader.pages:
            full_text += (page.extract_text() or "") + "\n\n"

        words = len(full_text.split())
        self.total_word_count += words
        self.doc_stats[filename] = {
            "name": filename,
            "format": "pdf",
            "word_count": words,
            "chunks_count": 0
        }

        # Chunk PDF by § sections
        pattern = r"(?=§\s*[\d\.]+)"
        raw_chunks = re.split(pattern, full_text)

        chunk_idx = 0
        for raw in raw_chunks:
            raw = raw.strip()
            if not raw:
                continue

            sec_match = re.search(r"§\s*([\d\.]+)\s*([^\n\r]+)", raw)
            if sec_match:
                sec_num = f"§ {sec_match.group(1).strip()}"
                sec_title = sec_match.group(2).strip()
                section_ref = f"Ordinance No. 14 {sec_num}"
                title = f"{sec_num} {sec_title}"
            else:
                section_ref = "Ordinance No. 14 Preamble"
                title = "Statutory Ordinance Notice"

            chunk = CorpusChunk(
                chunk_id=f"{filename}_{chunk_idx}",
                doc_name=filename,
                doc_title="Medi-Caps Ordinance No. 14: Examination Conduct & Board Powers",
                section_ref=section_ref,
                title=title,
                content=raw,
                doc_format="pdf"
            )
            self.chunks.append(chunk)
            chunk_idx += 1

        self.doc_stats[filename]["chunks_count"] = chunk_idx

    def _clean_doc_name(self, filename: str) -> str:
        if "academic" in filename:
            return "Academic Regulations"
        elif "hostel" in filename:
            return "Hostel Code of Conduct"
        elif "scholarship" in filename:
            return "Scholarship Policy"
        elif "fee" in filename:
            return "Fee Deadlines Schedule"
        elif "ordinance" in filename:
            return "Ordinance No. 14"
        return filename
