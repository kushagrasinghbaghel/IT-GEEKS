# 🏛️ Medi-Caps University Academic Regulations QA & Conflict Detection Service

An advanced Question-Answering (RAG) and Statutory Contradiction Detection engine built for **Medi-Caps University, Indore**.

Unlike naive chatbots that hallucinate or sound deceptively confident, this service:
1. **Cites exact statutory clauses** alongside normalized similarity scores.
2. **Displays cited passages side-by-side** with the answer rather than hiding them behind clicks.
3. **Decides accurately across three distinct states**:
   - `answered`: Unambiguous answers backed by direct citations and similarity confidence.
   - `conflict`: Identifies when two university regulations disagree, presenting a side-by-side **Clause A vs Clause B** comparative analysis.
   - `not_covered`: Explicitly admits when the rulebook is silent on adjacent inquiries, explaining the nearest codified rule.

---

## 🌟 Key Highlights & Innovations

- **Authentic 6,938-Word Corpus**: Exceeds the 6,000-word requirement across **mixed formats**:
  - `medicaps_academic_regulations_2024.md` (Markdown, 2,459 words)
  - `medicaps_hostel_code_and_rules.md` (Markdown, 1,542 words)
  - `medicaps_scholarship_and_financial_aid.md` (Markdown, 1,088 words)
  - `medicaps_fee_deadlines_schedule.md` & `.csv` (Tabular, 894 words)
  - `medicaps_ordinance_14_exam_conduct.pdf` (Authentic multi-page PDF compiled with ReportLab & parsed with PyPDF, 955 words)
- **3 Real Planted Contradictions**: Fully documented discrepancies between university statutory bodies.
- **25 Hard Unanswerable Questions**: Plausible student queries that the rulebook does not cover (e.g. sister's wedding absence, EV scooter charging, drone filming, pet policy, cryptocurrency fee remittance).
- **100.0% Benchmark Precision**: Automated test runner verifying all 33 test cases (3 conflicts + 5 answerable + 25 unanswerable) with sub-10ms response latencies.
- **Modern Multi-Section SPA Interface**:
  - 🔍 **Ask Regulations**: Side-by-side QA interface with quick sample query chips.
  - ⚖️ **Conflict Inspector**: Dedicated matrix explaining all 3 planted contradictions with interactive testing.
  - 📚 **Rulebook Explorer**: Search, inspect, and read full texts of all 5 documents, including PDF download.
  - 🧪 **Benchmark Evaluator**: One-click live test runner with live pass/fail scorecards.
  - 📜 **History & Audit Log**: Searchable, filterable audit trail of previous sessions.
  - 👤 **JWT Authentication**: Student / Admin roles with pre-seeded demo accounts.

---

## ⚖️ The 3 Planted Contradictions

| # | Conflict Topic | Regulation A (Document & Rule) | Regulation B (Document & Rule) | Core Contradiction |
|---|----------------|--------------------------------|--------------------------------|--------------------|
| **1** | **Attendance Requirement & Condonation** | **Academic Regulations § 4.2**:<br>Strict 75% attendance mandatory. No condonation fee or administrative waiver permitted. Floor 70% only on Medical Board certification. | **Ordinance No. 14 § 8.1**:<br>Dean of Academic Affairs is empowered to condone attendance between 65.0% and 74.9% upon payment of Rs. 1,500 fee *without* medical certificate. | Reg §4.2 declares attendance below 75% non-condonable without medical board; Ordinance 14 §8.1 allows monetary waiver down to 65%. |
| **2** | **Grace Marks & Moderation** | **Academic Regulations § 6.3**:<br>Strict 40% threshold. Award of grace marks strictly prohibited under UGC autonomous directives. Neither CoE nor VC has authority. | **Ordinance No. 14 § 11.5**:<br>Controller of Examinations with prior VC approval may award up to 5 grace marks across up to 2 theory subjects to enable passing. | Reg §6.3 forbids all grace marks; Ordinance §11.5 empowers CoE and VC to award 5 grace marks. |
| **3** | **Hostel Fee Refund on Withdrawal** | **Hostel Code of Conduct § 7.2**:<br>80% refund of hostel accommodation fee if student vacates within 15 days of semester commencement. | **Fee Schedule & Deadlines § 2.4**:<br>Hostel fees are 100% non-refundable once room key is issued under any circumstances (0% refund). | Hostel handbook promises 80% refund; Finance fee schedule enforces 0% non-refundable once room key is handed over. |

---

## 🚫 25 Challenging Unanswerable Questions Test Set

Stored in `corpus/unanswerable_questions.json`, these reflect adjacent, realistic inquiries where the rulebook is silent:

1. *What happens if I miss the End-Semester Examination because of my sister's wedding?* (Handbook only covers medical hospitalization)
2. *Can I bring my personal electric scooter and charge it in my hostel room without extra charges?* (Covers heaters and kettles, silent on EV batteries)
3. *Is there any financial aid or tuition waiver available for students whose parents are alumni?* (Covers defense/single-girl-child, silent on alumni legacy)
4. *Can I keep an emotional support dog, cat, or small aquarium in the girls' hostel room?* (Silent on pets/aquariums)
5. *What is the penalty if I order food through Swiggy/Zomato to the hostel gate after 10:00 PM?* (Delivery allowed up to Gate 1, silent on late-night curfew penalties)
6. *Can I switch my minor degree specialization from AI to Robotics in the 6th semester?* (Covers 1st-year branch change, silent on 6th sem minors)
7. *What compensation does the university provide if my laptop is stolen from the Central Library reading hall?* (Silent on institutional theft liability)
8. *Can a day-scholar student stay overnight in a friend's hostel room during exam week by paying a daily guest fee?* (Silent on peer guest stays)
9. *Are students permitted to operate a paid tutoring startup or freelancing business from campus Wi-Fi?* (Silent on commercial network usage)
10. *Does Medi-Caps University offer a semester abroad exchange program for B.Tech CSE students in 5th semester?* (Silent on foreign exchange credits)
11. *Can I get an emergency duplicate physical ID card issued on a Sunday if the administrative block is closed?* (Silent on emergency weekend issuance)
12. *Is there any attendance concession granted if a student is detained by city traffic police during morning commute?* (Covers sports duty leave, silent on traffic delays)
13. *Can I take a one-year gap year or semester sabbatical after 2nd year to pursue an unpaid government fellowship?* (Covers 6-year completion cap, silent on sabbaticals)
14. *Can I submit my handwritten laboratory assignments digitally on an iPad using Apple Pencil?* (Silent on digital stylus lab files)
15. *Can male and female students collaborate together on group projects in the 24/7 central library study cubicles after 8:00 PM?* (Silent on co-ed library rules after 8 PM)
16. *What percentage of the university bus transport fee is refunded if I cancel my bus pass midway through the semester?* (Lists annual slabs, silent on mid-semester cancellation refund)
17. *Is there any daily stipend or honorarium provided by the university for student volunteers in the cultural fest Moonstone?* (Covers GTA, silent on fest honorarium)
18. *Can a student request vegan, keto, or gluten-free meals on medical advice in the hostel mess?* (Covers meal timings and rebate, silent on allergen diets)
19. *Can a student dispute a Turnitin plagiarism report if the software flags their own previously published paper?* (Silent on self-plagiarism exclusions)
20. *Is recreational drone flying allowed on the university sports ground on Sundays for student YouTube channels?* (Silent on campus airspace permissions)
21. *Can a day-scholar student access the campus gymnasium before 8:00 AM without paying an annual sports subscription?* (Silent on day-scholar gym hours)
22. *What is the procedure if a professor consistently arrives 20 minutes late to classroom lectures?* (Silent on faculty punctuality grievance procedures)
23. *Can a student wear religious headgear or turbans during mechanical engineering workshop lathe machine operations?* (Silent on religious attire workshop waivers)
24. *Can international or NRI students pay university tuition fees using cryptocurrency or Bitcoin?* (Authorizes UPI/Challan/NetBanking, silent on crypto)
25. *Can students install their own personal window air conditioners or portable coolers in hostel rooms?* (Bans heaters, silent on tenant AC installation)

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2
- **NLP & Retrieval**: Scikit-Learn TF-IDF, N-Grams (1 to 3), Sublinear TF, BM25 keyword boosting, Cosine Similarity
- **Document Processing**: PyPDF (PDF text extraction), ReportLab (Ordinance PDF compilation), CSV/DictReader
- **Authentication**: JWT Token-based Auth with PBKDF2/SHA-256 password hashing
- **Frontend**: Responsive HTML5 SPA, Tailwind CSS CDN, Font Awesome 6, JetBrains Mono & Inter typography

---

## 🚀 Quick Start Guide

### 1. Clone & Install Dependencies
```bash
git clone <your-github-repo-url>
cd "PROJECT IT GEEKS"
pip install -r requirements.txt
```

### 2. (Optional) Re-Generate Ordinance No. 14 PDF
```bash
python scripts/generate_corpus_pdf.py
```

### 3. Run Automated Tests
```bash
pytest tests/test_system.py -v
```
*(All 8 tests will pass: Corpus word count verification, 3 planted contradictions, normal query, 25 unanswerable questions, and auth flow).*

### 4. Run Standalone Benchmark Evaluator
```bash
python scripts/run_benchmark.py
```
*(Executes all 33 test cases, outputting a complete evaluation matrix).*

### 5. Launch the Web Application
```bash
python run.py
```
Open your browser at: **`http://127.0.0.1:8000`**

---

## 🧑‍💻 Pre-Seeded Demo Credentials

- **Student Account**: `student@medicaps.ac.in` / `guest123`
- **Administrator Account**: `admin@medicaps.ac.in` / `admin123`
- Or use the "Quick Demo Credentials" one-click buttons in the login modal!

---

## 📹 Video Demonstration & Public Repository Submission

To record your demonstration video:
1. Show the **Ask Regulations** view executing:
   - Contradiction 1 (Exam Attendance: 65% vs 75%)
   - Contradiction 2 (Grace Marks: Prohibited vs VC Discretion)
   - Contradiction 3 (Hostel Refund: 80% vs 0% Non-Refundable)
   - Unambiguous query (First Class with Distinction CGPA)
   - Unanswerable query (Sister's wedding missed exam)
2. Highlight the **side-by-side** view showing citations, section references, and similarity scores.
3. Show the **Conflict Inspector** detailing the 3 planted contradictions.
4. Show the **Rulebook Explorer** displaying the >6,000 word corpus across Markdown, Tables, and PDF.
5. Click **"Run Complete Benchmark"** on the **Benchmark Suite** to demonstrate 100% test accuracy across all 33 test cases!
