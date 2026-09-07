"""
Script to generate an authentic Medi-Caps University Ordinance No. 14 PDF
using ReportLab.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable

def generate_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=1, # Center
        textColor=colors.HexColor('#0f2b48')
    )
    
    sub_title_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        alignment=1,
        textColor=colors.HexColor('#8b1d24')
    )
    
    h1_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#0f2b48'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    h2_style = ParagraphStyle(
        'ClauseHeading',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1f3a5f'),
        spaceBefore=8,
        spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#222222'),
        spaceAfter=5
    )
    
    alert_box_style = ParagraphStyle(
        'AlertBox',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#111827')
    )
    
    story = []
    
    # Header Banner
    story.append(Paragraph("MEDI-CAPS UNIVERSITY, INDORE", title_style))
    story.append(Paragraph("OFFICE OF THE REGISTRAR & CONTROLLER OF EXAMINATIONS", sub_title_style))
    story.append(Paragraph("Pigdambar, Rau, AB Road, Indore, Madhya Pradesh - 453331", ParagraphStyle('SubSub', alignment=1, fontSize=8, textColor=colors.gray)))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f2b48'), spaceAfter=15))
    
    # Ordinance metadata
    meta_data = [
        [Paragraph("<b>ORDINANCE NO. 14</b>", ParagraphStyle('M1', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#8b1d24'))),
         Paragraph("<b>Date of Gazetting:</b> July 10, 2024", ParagraphStyle('M2', fontName='Helvetica', fontSize=9, alignment=2))],
        [Paragraph("<b>Statutory Reference:</b> MCU/EXAM/ORD/14-REV", ParagraphStyle('M3', fontName='Helvetica', fontSize=9)),
         Paragraph("<b>Subject:</b> Conduct of Semester Examinations, Valuation, Condonation & Board Powers", ParagraphStyle('M4', fontName='Helvetica', fontSize=9, alignment=2))]
    ]
    t = Table(meta_data, colWidths=[260, 260])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f3f4f6')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))
    
    # Section 1
    story.append(Paragraph("CHAPTER I: PRELIMINARY APPOINTMENTS AND MODERATION", h1_style))
    story.append(Paragraph("§ 1.1 Question Paper Setting and Confidentiality", h2_style))
    story.append(Paragraph("1. Question papers for End-Semester Examinations shall be set by competent examiners appointed by the Vice-Chancellor from panels recommended by the respective Boards of Studies.", body_style))
    story.append(Paragraph("2. Paper setters must submit two distinct sets of question papers along with full answer keys in sealed tamper-proof envelopes to the Controller of Examinations at least thirty (30) days prior to the commencement of examinations.", body_style))
    story.append(Paragraph("3. All question papers must align with the prescribed Course Outcomes (COs) and Bloom's Revised Taxonomy levels as stipulated by the National Board of Accreditation (NBA).", body_style))
    
    story.append(Paragraph("§ 1.2 Moderation Board Functions", h2_style))
    story.append(Paragraph("1. A Question Paper Moderation Board consisting of the Dean of Faculty, Head of Department, and one senior external professor shall scrutinize paper sets to ensure adherence to syllabus boundaries, mark distributions, and absence of ambiguity.", body_style))
    story.append(Paragraph("2. The Moderation Board is empowered to rectify factual errors or rephrase ambiguous clauses but cannot substitute more than 20% of total questions.", body_style))
    
    # Section 2
    story.append(Spacer(1, 10))
    story.append(Paragraph("CHAPTER II: EXAMINATION HALL PROTOCOLS AND SUPERVISION", h1_style))
    story.append(Paragraph("§ 2.1 Center Superintendent and Invigilator Responsibilities", h2_style))
    story.append(Paragraph("1. The Center Superintendent shall be in operational charge of the examination center, ensuring secure custodial maintenance of question paper packets, answer booklets, and dispatch logs.", body_style))
    story.append(Paragraph("2. Invigilators shall report to the center at least 45 minutes before commencement. One invigilator shall be deployed per twenty-five (25) examinees.", body_style))
    story.append(Paragraph("3. Examinees must occupy designated seats 15 minutes before exam commencement. No candidate is allowed entry 30 minutes after the exam commences, nor permitted to exit before the lapse of two hours.", body_style))
    
    # Section 3
    story.append(Spacer(1, 10))
    story.append(Paragraph("CHAPTER III: UNFAIR MEANS (UFM) DISCIPLINARY MECHANISM", h1_style))
    story.append(Paragraph("§ 3.1 Classification of Unfair Means (UFM)", h2_style))
    story.append(Paragraph("1. <b>Category A (Minor Infractions):</b> Possession of paper notes, mathematical formulas scribbled on palms, calculators, or rulers without intent to circulate. Penalty: Cancellation of performance in the concerned paper.", body_style))
    story.append(Paragraph("2. <b>Category B (Major Malpractice):</b> Possession of active mobile devices, smart watches, wireless earbuds, copying from neighbor, or passing chits. Penalty: Cancellation of entire semester examination performance.", body_style))
    story.append(Paragraph("3. <b>Category C (Criminal Impersonation & Violence):</b> Impersonation of another examinee, tampering with answer booklets, or intimidating invigilation staff. Penalty: Permanent debarment from Medi-Caps University and filing of a First Information Report (FIR) under the MP Recognized Examinations Act.", body_style))
    
    story.append(PageBreak()) # PAGE 2
    
    story.append(Paragraph("CHAPTER IV: ATTENDANCE SHORTFALL CONDONATION POWERS", h1_style))
    story.append(Paragraph("§ 8.1 Statutory Condonation by Dean of Academic Affairs (PLANTED CONTRADICTION 1)", h2_style))
    story.append(Paragraph("1. <b>Statutory Discretion of Dean:</b> Notwithstanding any general academic attendance rules or departmental regulations, the Dean of Academic Affairs is vested with statutory discretionary authority to condone attendance shortage for students whose cumulative semester attendance in any subject falls between 65.0% and 74.9%.", body_style))
    story.append(Paragraph("2. <b>Condonation Fee Procedure:</b> Such condonation shall be granted upon the student submitting a standard Form-Condonation application to the Academic Office accompanied by payment of a prescribed Condonation Fee of Rs. 1,500 per subject to the University Accounts Branch.", body_style))
    story.append(Paragraph("3. <b>No Medical Certificate Mandate:</b> Under this statutory provision, students falling within the 65.0% to 74.9% bracket are NOT required to present medical board certificates or hospital inpatient documentation. Upon payment of the prescribed condonation fee and endorsement by the Dean of Academic Affairs, the Controller of Examinations shall issue an unrestricted examination admit card.", body_style))
    story.append(Paragraph("4. <i>Administrative Precedence Note:</i> The statutory authority granted under this Ordinance is enacted pursuant to Executive Council directives and supersedes ordinary departmental minimum attendance barriers.", body_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("CHAPTER V: CENTRAL EVALUATION AND TABULATION", h1_style))
    story.append(Paragraph("§ 9.1 Coding, Decoding, and Evaluation", h2_style))
    story.append(Paragraph("1. All answer booklets shall have their student identity flaps masked and replaced with computerized dummy barcodes before distribution to valuation tables.", body_style))
    story.append(Paragraph("2. Evaluators must complete grading within seven (7) working days of receiving scripts. The maximum number of scripts an examiner can evaluate in a single working day is sixty (60).", body_style))
    story.append(Paragraph("3. Marks awarded shall be directly uploaded into the secured Central Valuation Server using encrypted biometric authorization.", body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("CHAPTER VI: EXAMINATION RESULTS AND GRACE MARKS DISCRETION", h1_style))
    story.append(Paragraph("§ 11.5 Statutory Discretion for Award of Grace Marks (PLANTED CONTRADICTION 2)", h2_style))
    story.append(Paragraph("1. <b>Vice-Chancellor and CoE Discretionary Moderation:</b> Notwithstanding any general passing threshold or autonomous departmental grading guideline, the Controller of Examinations, with the prior written sanction of the Vice-Chancellor, is empowered to award up to a maximum of five (5) grace marks to a candidate who fails in not more than two (2) theory subjects in any regular semester examination.", body_style))
    story.append(Paragraph("2. <b>Application of Grace Marks:</b> The grace marks may be split across two failing subjects (e.g., 3 marks in Subject A and 2 marks in Subject B) or applied in full (up to 5 marks) to a single subject to elevate the candidate's score to the statutory passing benchmark of 40 marks out of 100.", body_style))
    story.append(Paragraph("3. <b>Mark Sheet Notation:</b> A student who passes a course with the assistance of grace marks shall have the symbol 'G' appended next to their course grade in the final grade card, indicating passed with moderation.", body_style))
    story.append(Paragraph("4. <b>Autonomous Board Competence:</b> This moderating prerogative is instituted to protect academic progression against marginal failure and overrides general prohibitions against moderation.", body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("CHAPTER VII: ARCHIVAL AND SCRIPT RETENTION", h1_style))
    story.append(Paragraph("§ 12.1 Script Storage and Disposal", h2_style))
    story.append(Paragraph("1. All physically evaluated answer booklets must be preserved in the Examination Confidential Strong Room for a minimum period of three (3) calendar years from the date of result declaration.", body_style))
    story.append(Paragraph("2. Following the expiry of the three-year retention period, answer booklets may be disposed of through industrial paper pulping under the supervision of a three-member Disposal Committee constituted by the Registrar.", body_style))

    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0f2b48'), spaceAfter=10))
    
    signatures = [
        [Paragraph("<b>Prof. (Dr.) Rajesh Sharma</b><br/>Controller of Examinations", ParagraphStyle('S1', fontSize=9)),
         Paragraph("<b>Dr. Anurag Verma</b><br/>Dean, Academic Affairs", ParagraphStyle('S2', fontSize=9, alignment=1)),
         Paragraph("<b>Prof. (Dr.) Dilip Kumar</b><br/>Registrar, Medi-Caps University", ParagraphStyle('S3', fontSize=9, alignment=2))]
    ]
    st = Table(signatures, colWidths=[170, 170, 180])
    st.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(st)
    
    doc.build(story)
    print(f"Ordinance 14 PDF generated successfully at: {output_path}")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "..", "corpus")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "medicaps_ordinance_14_exam_conduct.pdf")
    generate_pdf(out_file)
