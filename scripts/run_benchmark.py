"""
Standalone Benchmark Runner for Medi-Caps Academic Regulations QA System.
Runs all 33 test cases:
- 3 Planted Contradictions
- 5 Standard Answerable Queries
- 25 Hard Unanswerable Queries
Prints a formatted evaluation report.
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag_engine import RAGEngine
from app.corpus_loader import CorpusLoader

def main():
    print("=" * 80)
    print("  MEDI-CAPS UNIVERSITY ACADEMIC REGULATIONS QA BENCHMARK EVALUATOR")
    print("=" * 80)

    loader = CorpusLoader()
    print(f"Corpus Loaded: {loader.total_word_count} words across {len(loader.doc_stats)} documents ({len(loader.chunks)} chunks)")
    print(f"Meets >6,000 words requirement: {'YES [PASS]' if loader.total_word_count >= 6000 else 'NO [FAIL]'}")
    print("-" * 80)

    engine = RAGEngine(loader)

    test_cases = [
        # 3 Planted Contradictions
        {
            "category": "conflict",
            "query": "Can attendance between 65% and 75% be condoned by paying a fee without medical certificate?",
            "expected": "conflict",
            "title": "Contradiction 1: Exam Attendance Condonation (Reg §4.2 vs Ord 14 §8.1)"
        },
        {
            "category": "conflict",
            "query": "Can the Vice Chancellor or Controller of Examinations award grace marks if I am failing a subject?",
            "expected": "conflict",
            "title": "Contradiction 2: Grace Marks Prohibition vs VC Powers (Reg §6.3 vs Ord 14 §11.5)"
        },
        {
            "category": "conflict",
            "query": "What percentage of hostel accommodation fee is refunded if I cancel within 15 days of semester start?",
            "expected": "conflict",
            "title": "Contradiction 3: Hostel 80% Refund vs 0% Non-Refundable (Hostel §7.2 vs Fee §2.4)"
        },
        # 5 Standard Answerable Queries
        {
            "category": "answered",
            "query": "What is the minimum CGPA required to graduate with First Class with Distinction?",
            "expected": "answered",
            "title": "Query A: First Class with Distinction Criteria"
        },
        {
            "category": "answered",
            "query": "What are the eligibility criteria and minimum CGPA for B.Tech branch change after first year?",
            "expected": "answered",
            "title": "Query B: First Year Branch Change Policy"
        },
        {
            "category": "answered",
            "query": "What is the tuition fee concession percentage for dependent children of defense personnel?",
            "expected": "answered",
            "title": "Query C: Defense Wards Tuition Fee Concession"
        },
        {
            "category": "answered",
            "query": "What are the curfew entry timings for boys and girls hostels on weekdays?",
            "expected": "answered",
            "title": "Query D: Hostel Curfew and Gate Timings"
        },
        {
            "category": "answered",
            "query": "What is the fee and timeline for challenge re-evaluation of answer scripts?",
            "expected": "answered",
            "title": "Query E: Challenge Re-Evaluation Procedure & Fee"
        }
    ]

    # Add all 25 unanswerable questions
    for u in engine.unanswerable_dataset:
        test_cases.append({
            "category": "not_covered",
            "query": u["question"],
            "expected": "not_covered",
            "title": f"Unanswerable #{u['id']}: {u['question'][:45]}..."
        })

    total = len(test_cases)
    passed = 0
    latencies = []

    print(f"\nRunning {total} Benchmark Evaluations...\n")
    print(f"{'#':<3} | {'Category':<12} | {'Expected':<12} | {'Actual':<12} | {'Status':<7} | {'Latency':<7} | Title")
    print("-" * 88)

    for i, t in enumerate(test_cases, 1):
        t0 = time.time()
        res = engine.ask(t["query"])
        latency = (time.time() - t0) * 1000
        latencies.append(latency)

        actual = res["verdict"]
        is_ok = (actual == t["expected"])
        if is_ok:
            passed += 1

        status_str = "[PASS]" if is_ok else "[FAIL]"
        print(f"{i:<3} | {t['category']:<12} | {t['expected']:<12} | {actual:<12} | {status_str:<7} | {latency:>5.1f}ms | {t['title']}")

    accuracy = (passed / total) * 100.0
    avg_latency = sum(latencies) / len(latencies)

    print("=" * 88)
    print(f"BENCHMARK SUMMARY:")
    print(f"Total Test Cases:       {total}")
    print(f"Passed:                 {passed}")
    print(f"Failed:                 {total - passed}")
    print(f"Accuracy:               {accuracy:.2f}%")
    print(f"Average Response Time:  {avg_latency:.2f} ms")
    print("=" * 88)

if __name__ == "__main__":
    main()
