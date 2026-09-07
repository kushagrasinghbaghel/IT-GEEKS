"""
FastAPI Application for Medi-Caps University Academic Regulations QA Service.
Endpoints:
- POST /ask: Main QA endpoint returning answered, conflict, or not_covered.
- GET /corpus/stats, /corpus/documents, /corpus/document/{doc_name}
- GET /contradictions, /unanswerable
- POST /benchmark/run
- POST /auth/login, /auth/register, /auth/me
- GET /history, DELETE /history
"""
import os
import time
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import CORPUS_DIR, STATIC_DIR, UNIVERSITY_NAME
from app.corpus_loader import CorpusLoader
from app.rag_engine import RAGEngine
from app.auth import AuthManager
from app.history import HistoryManager

# Initialize Core Services
app = FastAPI(
    title="Medi-Caps University Regulations QA & Conflict Detection API",
    description="Autonomous RAG QA service over Medi-Caps University academic regulations, featuring multi-source citation and conflict detection.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

corpus_loader = CorpusLoader(CORPUS_DIR)
rag_engine = RAGEngine(corpus_loader)
auth_manager = AuthManager()
history_manager = HistoryManager()

# Mount Static Files
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Request / Response Schemas
class AskRequest(BaseModel):
    query: str = Field(..., json_schema_extra={"example": "Can attendance between 65% and 75% be condoned by paying a fee?"})

class CitationItem(BaseModel):
    section_ref: str
    doc_name: str
    title: str
    excerpt: str
    similarity_score: float
    format: str

class AskResponse(BaseModel):
    status: str
    verdict: str  # "answered" | "conflict" | "not_covered"
    query: str
    answer: str
    conflict_details: Optional[Dict[str, Any]] = None
    citations: List[CitationItem]
    latency_ms: float
    user: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    enrollment_no: str
    department: str = "Computer Science & Engineering"

# Dependency: Extract user from Authorization Header if present
def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    if not authorization:
        return None
    token = authorization.replace("Bearer ", "").strip()
    return auth_manager.verify_token(token)

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Medi-Caps University QA Service is Running</h1><p>UI loading...</p>")

@app.post("/ask", response_model=AskResponse)
async def ask_endpoint(payload: AskRequest, current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """
    Main QA Endpoint over Medi-Caps University Rulebook Corpus.
    Returns:
    - 'answered': when unambiguous rules are cited with similarity scores.
    - 'conflict': when two or more clauses directly contradict each other.
    - 'not_covered': when the corpus is silent on an adjacent inquiry.
    """
    if not payload.query or not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query text cannot be empty.")

    start_time = time.time()
    result = rag_engine.ask(payload.query.strip())
    latency = (time.time() - start_time) * 1000

    user_email = current_user["email"] if current_user else "guest@medicaps.ac.in"

    # Record in history
    history_manager.add_entry(
        query=result["query"],
        verdict=result["verdict"],
        answer=result["answer"],
        citations=result["citations"],
        latency_ms=latency,
        user_email=user_email,
        conflict_details=result.get("conflict_details")
    )

    return AskResponse(
        status=result["status"],
        verdict=result["verdict"],
        query=result["query"],
        answer=result["answer"],
        conflict_details=result.get("conflict_details"),
        citations=result["citations"],
        latency_ms=round(latency, 2),
        user=user_email
    )

# Corpus Endpoints
@app.get("/corpus/stats")
async def get_corpus_stats():
    return {
        "university": UNIVERSITY_NAME,
        "total_words": corpus_loader.total_word_count,
        "meets_minimum_requirement": corpus_loader.total_word_count >= 6000,
        "total_chunks": len(corpus_loader.chunks),
        "total_documents": len(corpus_loader.doc_stats),
        "documents": corpus_loader.doc_stats,
        "planted_contradictions_count": len(rag_engine.conflict_detector.known_conflicts),
        "unanswerable_benchmark_count": len(rag_engine.unanswerable_dataset)
    }

@app.get("/corpus/documents")
async def get_corpus_documents():
    return list(corpus_loader.doc_stats.values())

@app.get("/corpus/document/{doc_name}")
async def get_corpus_document_content(doc_name: str):
    safe_name = os.path.basename(doc_name)
    filepath = os.path.join(CORPUS_DIR, safe_name)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Document {safe_name} not found.")

    if safe_name.endswith(".pdf"):
        # For PDF, extract full text or serve raw file
        from pypdf import PdfReader
        reader = PdfReader(filepath)
        text = "\n\n".join([f"--- PAGE {i+1} ---\n" + (p.extract_text() or "") for i, p in enumerate(reader.pages)])
        return {
            "name": safe_name,
            "format": "pdf",
            "content": text,
            "pdf_url": f"/corpus/download/{safe_name}"
        }
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return {
            "name": safe_name,
            "format": "markdown" if safe_name.endswith(".md") else "tabular",
            "content": content
        }

@app.get("/corpus/download/{doc_name}")
async def download_corpus_file(doc_name: str):
    safe_name = os.path.basename(doc_name)
    filepath = os.path.join(CORPUS_DIR, safe_name)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File {safe_name} not found.")
    return FileResponse(filepath, filename=safe_name)

@app.get("/contradictions")
async def get_contradictions():
    return rag_engine.conflict_detector.known_conflicts

@app.get("/unanswerable")
async def get_unanswerable_questions():
    return rag_engine.unanswerable_dataset

# Benchmark Runner
@app.post("/benchmark/run")
async def run_benchmark():
    """
    Executes the full evaluation test suite:
    - 3 Planted Contradictions
    - 5 Standard Answerable Queries
    - 25 Hard Unanswerable Queries
    Returns accuracy, latency, and detailed test outputs.
    """
    test_cases = [
        # 3 Planted Contradictions
        {
            "category": "conflict",
            "query": "Can attendance between 65% and 75% be condoned by paying a fee?",
            "expected_verdict": "conflict",
            "title": "Contradiction 1: Exam Attendance Condonation"
        },
        {
            "category": "conflict",
            "query": "Are grace marks awarded to pass students failing by a few marks in semester exams?",
            "expected_verdict": "conflict",
            "title": "Contradiction 2: Grace Marks Prohibition vs VC Discretion"
        },
        {
            "category": "conflict",
            "query": "What refund percentage do I get if I vacate the hostel within 15 days of semester commencement?",
            "expected_verdict": "conflict",
            "title": "Contradiction 3: Hostel Fee 80% Refund vs 0% Non-Refundable"
        },
        # 5 Standard Answerable Queries
        {
            "category": "answered",
            "query": "What is the minimum CGPA required to graduate with First Class with Distinction?",
            "expected_verdict": "answered",
            "title": "First Class with Distinction Criteria"
        },
        {
            "category": "answered",
            "query": "What are the eligibility criteria and minimum CGPA for B.Tech branch change after first year?",
            "expected_verdict": "answered",
            "title": "Branch Change Policy"
        },
        {
            "category": "answered",
            "query": "What is the tuition fee concession percentage for dependent children of defense personnel?",
            "expected_verdict": "answered",
            "title": "Defense Wards Scholarship Scheme"
        },
        {
            "category": "answered",
            "query": "What are the curfew entry timings for boys and girls hostels on weekdays?",
            "expected_verdict": "answered",
            "title": "Hostel Curfew and Gate Timings"
        },
        {
            "category": "answered",
            "query": "What is the fee and timeline for challenge re-evaluation of answer scripts?",
            "expected_verdict": "answered",
            "title": "Challenge Re-Evaluation Procedure"
        }
    ]

    # Add all 25 unanswerable questions
    for u in rag_engine.unanswerable_dataset:
        test_cases.append({
            "category": "not_covered",
            "query": u["question"],
            "expected_verdict": "not_covered",
            "title": f"Unanswerable #{u['id']}: {u['question'][:40]}..."
        })

    total = len(test_cases)
    passed = 0
    results = []
    latencies = []

    for t in test_cases:
        t0 = time.time()
        res = rag_engine.ask(t["query"])
        latency = (time.time() - t0) * 1000
        latencies.append(latency)

        is_correct = (res["verdict"] == t["expected_verdict"])
        if is_correct:
            passed += 1

        results.append({
            "title": t["title"],
            "query": t["query"],
            "category": t["category"],
            "expected": t["expected_verdict"],
            "actual": res["verdict"],
            "passed": is_correct,
            "citations_count": len(res.get("citations", [])),
            "latency_ms": round(latency, 2),
            "answer_snippet": res["answer"][:160] + "..."
        })

    accuracy = (passed / total) * 100.0 if total > 0 else 0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    return {
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": total - passed,
        "accuracy_percentage": round(accuracy, 2),
        "average_latency_ms": round(avg_latency, 2),
        "breakdown": {
            "conflicts": {
                "total": 3,
                "passed": sum(1 for r in results if r["category"] == "conflict" and r["passed"])
            },
            "answered": {
                "total": 5,
                "passed": sum(1 for r in results if r["category"] == "answered" and r["passed"])
            },
            "not_covered": {
                "total": 25,
                "passed": sum(1 for r in results if r["category"] == "not_covered" and r["passed"])
            }
        },
        "results": results
    }

# Auth Endpoints
@app.post("/auth/login")
async def login(payload: LoginRequest):
    res = auth_manager.authenticate(payload.email, payload.password)
    if not res["success"]:
        raise HTTPException(status_code=401, detail=res["error"])
    return res

@app.post("/auth/register")
async def register(payload: RegisterRequest):
    res = auth_manager.register(
        email=payload.email,
        password=payload.password,
        name=payload.name,
        enrollment_no=payload.enrollment_no,
        department=payload.department
    )
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@app.get("/auth/me")
async def get_me(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return current_user

# History Endpoints
@app.get("/history")
async def get_history(
    verdict: Optional[str] = "all",
    search: Optional[str] = None,
    limit: int = 50
):
    return history_manager.get_entries(verdict=verdict, search=search, limit=limit)

@app.delete("/history")
async def clear_history():
    history_manager.clear()
    return {"status": "success", "message": "History cleared successfully"}
