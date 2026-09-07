"""
Comprehensive Test Suite for Medi-Caps Academic Regulations QA & Conflict System.
Run via: pytest tests/test_system.py -v
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from app.main import app, corpus_loader, rag_engine

client = TestClient(app)

def test_corpus_word_count_requirement():
    """Verify the corpus contains at least 6,000 words across mixed formats."""
    total_words = corpus_loader.total_word_count
    assert total_words >= 6000, f"Corpus only has {total_words} words; minimum required is 6,000"
    
    # Verify formats
    formats = set(d["format"] for d in corpus_loader.doc_stats.values())
    assert "markdown" in formats
    assert "pdf" in formats
    assert "tabular_csv" in formats

def test_post_ask_normal_query():
    """Verify an unambiguous question is answered with valid citations and similarity score."""
    payload = {"query": "What is the minimum CGPA required to graduate with First Class with Distinction?"}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["verdict"] == "answered"
    assert len(data["citations"]) > 0
    # Similarity score must be positive and <= 1.0
    for c in data["citations"]:
        assert 0.0 <= c["similarity_score"] <= 1.0
        assert c["section_ref"] != ""

def test_planted_contradiction_1_attendance():
    """Verify attendance condonation discrepancy triggers conflict."""
    payload = {"query": "Can attendance between 65% and 75% be condoned by paying a fee without medical certificate?"}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "conflict"
    assert data["conflict_details"] is not None
    assert "contradiction_attendance_condonation" in data["conflict_details"]["conflict_id"]
    # Check that both conflicting clauses are returned
    assert "clause_a" in data["conflict_details"]
    assert "clause_b" in data["conflict_details"]

def test_planted_contradiction_2_grace_marks():
    """Verify grace marks discrepancy triggers conflict."""
    payload = {"query": "Can the Vice Chancellor or Controller of Examinations award grace marks if I am failing a subject?"}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "conflict"
    assert data["conflict_details"] is not None
    assert "contradiction_grace_marks" in data["conflict_details"]["conflict_id"]

def test_planted_contradiction_3_hostel_refund():
    """Verify hostel cancellation fee refund discrepancy triggers conflict."""
    payload = {"query": "What percentage of hostel accommodation fee is refunded if I cancel within 15 days of semester start?"}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "conflict"
    assert data["conflict_details"] is not None
    assert "contradiction_hostel_fee_refund" in data["conflict_details"]["conflict_id"]

def test_all_25_unanswerable_questions():
    """Verify that all 25 adjacent hard unanswerable questions are correctly classified as not_covered."""
    unanswerable_list = rag_engine.unanswerable_dataset
    assert len(unanswerable_list) == 25, f"Expected 25 unanswerable questions, got {len(unanswerable_list)}"

    for item in unanswerable_list:
        payload = {"query": item["question"]}
        response = client.post("/ask", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["verdict"] == "not_covered", f"Failed for question: {item['question']}, got: {data['verdict']}"

def test_benchmark_endpoint():
    """Verify the /benchmark/run endpoint executes and yields high accuracy."""
    response = client.post("/benchmark/run")
    assert response.status_code == 200
    data = response.json()
    assert data["total_tests"] >= 33 # 3 conflicts + 5 answered + 25 not covered
    assert data["accuracy_percentage"] >= 95.0
    assert data["breakdown"]["conflicts"]["passed"] == 3
    assert data["breakdown"]["not_covered"]["passed"] == 25

def test_auth_and_history_flow():
    """Verify user registration, login, and query history persistence."""
    # Test demo login
    login_resp = client.post("/auth/login", json={"email": "student@medicaps.ac.in", "password": "guest123"})
    assert login_resp.status_code == 200
    token = login_resp.json()["token"]
    assert token is not None

    # Check /auth/me
    me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "student@medicaps.ac.in"

    # Check history
    hist_resp = client.get("/history")
    assert hist_resp.status_code == 200
    assert isinstance(hist_resp.json(), list)
