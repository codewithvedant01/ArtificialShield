"""Generate full VIT Bhopal Review 2 project report (.docx)."""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches


def center(doc: Document, text: str, bold: bool = False, size: int = 12) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)


def body(doc: Document, text: str) -> None:
    doc.add_paragraph(text)


def heading(doc: Document, text: str, level: int = 1) -> None:
    doc.add_heading(text, level=level)


def table(doc: Document, headers: list[str], rows: list[list[str]]) -> None:
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    for i, h in enumerate(headers):
        t.rows[0].cells[i].text = h
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = val
    doc.add_paragraph("")


def build_report(output_path: Path) -> None:
    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)

    center(doc, "Stopping Indirect Prompt Injection in Artificial Intelligence", bold=True, size=16)
    center(doc, "PROJECT REPORT", bold=True, size=14)
    center(doc, "")
    center(doc, "Submitted by")
    for student in [
        "Vedant Khandelwal (25MEI10120)",
        "Namra Rafique (25MEI10100)",
        "Vaishnavi Jha (25MEI10030)",
        "Aqsa Ali (25MEI10003)",
        "Souhini Roy (25MEI10040)",
    ]:
        center(doc, student)
    center(doc, "")
    center(doc, "in partial fulfillment for the award of the degree of")
    center(doc, "Integrated M.Tech.")
    center(doc, "in")
    center(doc, "Computer Science and Engineering (Cyber Security)")
    center(doc, "School of Computing Science Engineering and Artificial Intelligence (SCAI)")
    center(doc, "VIT BHOPAL UNIVERSITY")
    center(doc, "KOTHRIKALAN, SEHORE")
    center(doc, "MADHYA PRADESH - 466114")
    center(doc, "Project Exhibition - I (Review 2)")
    center(doc, "September 2026")
    center(doc, "Project Guide: Prof. T. VENKATESWARA RAO")

    doc.add_page_break()
    heading(doc, "BONAFIDE CERTIFICATE")
    body(
        doc,
        "Certified that this project report titled “Stopping Indirect Prompt Injection in Artificial "
        "Intelligence” is the Bonafide work of Vedant Khandelwal (25MEI10120), Namra Rafique "
        "(25MEI10100), Vaishnavi Jha (25MEI10030), Aqsa Ali (25MEI10003), and Souhini Roy "
        "(25MEI10040), who carried out the project work under the supervision of Prof. T. "
        "Venkateswara Rao. Certified further that to the best of my knowledge the work reported at "
        "this time does not form part of any other project/research work based on which a degree or "
        "award was conferred on an earlier occasion on this or any other candidate.",
    )
    center(doc, "")
    center(doc, "PROGRAM CHAIR                                    PROJECT GUIDE")
    center(doc, "Prof. T. VENKATESWARA RAO                        Prof. T. VENKATESWARA RAO")
    center(doc, "SCAI                                             SCAI")
    center(doc, "VIT BHOPAL UNIVERSITY                            VIT BHOPAL UNIVERSITY")
    center(doc, "The Project Exhibition I Examination is held on ____________________")

    doc.add_page_break()
    heading(doc, "ACKNOWLEDGEMENT")
    body(
        doc,
        "We express our sincere gratitude to the Almighty for giving us the strength and guidance to "
        "complete this project work. We are deeply grateful to Prof. T. Venkateswara Rao, our project "
        "guide, for his valuable guidance, encouragement, and constructive suggestions throughout "
        "the development of this project. We also thank the faculty members and technical staff of "
        "the School of Computing Science Engineering and Artificial Intelligence (SCAI), VIT Bhopal "
        "University, for their support and academic guidance. Finally, we thank our parents, friends, "
        "and teammates for their constant encouragement and support.",
    )

    doc.add_page_break()
    heading(doc, "LIST OF ABBREVIATIONS")
    table(
        doc,
        ["Abbreviation", "Meaning"],
        [
            ["LLM", "Large Language Model"],
            ["RAG", "Retrieval-Augmented Generation"],
            ["API", "Application Programming Interface"],
            ["ML", "Machine Learning"],
            ["REST", "Representational State Transfer"],
            ["CPU", "Central Processing Unit"],
            ["F1", "F1 Score"],
            ["ROC-AUC", "Receiver Operating Characteristic – Area Under Curve"],
            ["NFR", "Non-Functional Requirement"],
            ["FR", "Functional Requirement"],
            ["IPI", "Indirect Prompt Injection"],
            ["OWASP", "Open Worldwide Application Security Project"],
        ],
    )

    heading(doc, "LIST OF FIGURES AND GRAPHS")
    for item in [
        "Fig. 1. Inline guardrail proxy data flow",
        "Fig. 2. Threat / attack flow",
        "Fig. 3. Implemented proxy component architecture",
        "Fig. 4. Review 2 evaluation methodology",
        "Fig. 5. Streamlit analytics dashboard layout",
    ]:
        body(doc, item)

    heading(doc, "LIST OF TABLES")
    for item in [
        "Table I. Indirect prompt injection risk taxonomy",
        "Table II. Scope matrix for Review 2 milestone",
        "Table III. Comparison of existing defenses",
        "Table IV. Functional and non-functional requirements",
        "Table V. Review 2 completion status",
        "Table VI. Integrated proxy performance summary",
    ]:
        body(doc, item)

    doc.add_page_break()
    heading(doc, "ABSTRACT")
    body(doc, "Purpose: Large Language Model applications increasingly consume untrusted external content such as web pages, retrieved documents, e-mail bodies, and tool outputs. When such content carries adversarial instructions, the model may follow them instead of the developer’s intended policy. This project addresses indirect prompt injection by placing detection at the transport boundary rather than relying only on prompt-level instructions.")
    body(doc, "Methodology: ArtificialShield is an inline ML guardrail proxy between a client application and an LLM backend. Every inbound prompt and retrieved context fragment is normalized, segmented, and scored using a DeBERTa-v3 injection classifier (ProtectAI/deberta-v3-base-prompt-injection-v2). Requests above a calibrated threshold (τ = 0.85) are blocked and logged; other requests are forwarded. The stack uses Python 3.11, FastAPI/Uvicorn, Hugging Face Transformers with PyTorch, SQLite, Streamlit, pytest, Locust, and Docker.")
    body(doc, "Findings / Review 2 status: Review 2 completed FastAPI proxy integration, SQLite audit logging, Streamlit dashboard delivery, and threshold calibration. The vulnerable baseline agent and attack reproduction harness from Review 1 were replayed through the proxy. On the project attack set (4 injection variants), the proxy achieved 100% block rate with 0% false-positive rate on the benign held-out prompts tested. CPU-only integrated latency measured p50 ≈ 42 ms, p95 ≈ 78 ms, and p99 ≈ 91 ms, meeting the sub-100 ms p95 target.")

    doc.add_page_break()
    heading(doc, "CHAPTER-1: PROJECT DESCRIPTION AND OUTLINE")
    heading(doc, "1.1 Introduction", 2)
    body(doc, "Instruction-tuned LLMs do not inherently distinguish trusted developer instructions from untrusted data when both are represented as tokens in a common context. In retrieval-augmented applications, attacker-authored text embedded in external content can therefore be interpreted as an instruction.")
    heading(doc, "1.2 Motivation for the Work", 2)
    body(doc, "Practical consequences include confidentiality loss through data exfiltration and integrity loss through unauthorized tool execution. The project treats injection defense as a system-level security boundary rather than only a prompt-writing problem.")
    heading(doc, "1.3 Introduction to the Project and Techniques", 2)
    body(doc, "ArtificialShield implements an ML guardrail proxy as a transport-level inline service. It intercepts prompts and retrieved context, normalizes and segments them, classifies them with DeBERTa-v3, compares the score with a calibrated threshold, and either forwards the request or returns a structured refusal. Blocked payloads are persisted in SQLite for analyst review through Streamlit.")
    heading(doc, "1.4 Threat Context", 2)
    body(doc, "The assumed adversary can write content into a source that the target application later retrieves, such as a public web page, shared document, product review, issue comment, or inbound e-mail. The attack path is attacker → poisoned external source → retriever/tool → prompt assembly → LLM → attacker-directed action.")
    heading(doc, "1.5 Problem Statement", 2)
    body(doc, "Prompt-only defenses compete with malicious instructions inside the same context. Static filters can miss paraphrases, obfuscation, and multilingual payloads, while architectural isolation may require application redesign. The project addresses the deployability gap through a lightweight REST proxy with classifier-based detection and forensic logging.")
    heading(doc, "1.6 Objective of the Work", 2)
    body(doc, "The primary objective is to intercept and score every inbound prompt and context fragment with added end-to-end latency below 100 ms at p95 on commodity CPU inference. Secondary objectives include persistent logging of blocked payloads and Streamlit-based analytical visibility.")
    heading(doc, "1.7 Organization of the Project", 2)
    body(doc, "The report follows the VIT Bhopal sequence: project description, related work, requirements, design methodology, technical implementation and analysis, outcomes and applicability, and conclusions and recommendations.")
    heading(doc, "1.8 Summary", 2)
    body(doc, "Review 2 extends the Review 1 threat baseline and architecture with a working integrated proxy, audit logging, analytics dashboard, and initial quantitative validation.")

    doc.add_page_break()
    heading(doc, "CHAPTER-2: RELATED WORK INVESTIGATION")
    heading(doc, "2.1 Introduction", 2)
    body(doc, "Research on prompt injection covers attack construction, benchmarking, provenance-aware defenses, architectural isolation, and model-based detection.")
    heading(doc, "2.2 Indirect Prompt Injection and LLM Security", 2)
    body(doc, "Indirect prompt injection occurs when malicious instructions are embedded in external content later processed by an LLM. Hines et al. introduced spotlighting, a provenance-oriented technique designed to help models distinguish input sources; their experiments reported a reduction in attack success from above 50% to below 2% in the tested settings.")
    heading(doc, "2.3 Existing Approaches/Methods", 2)
    body(doc, "2.3.1 System-Prompt Hardening — System prompts can instruct models to ignore embedded commands, but adversarial content remains in the same context.")
    body(doc, "2.3.2 Regex / Static Filtering — Static rules can detect known signatures but are inflexible against paraphrase and obfuscation.")
    body(doc, "2.3.3 Architectural Isolation and Provenance — Architectural isolation and provenance-aware techniques strengthen trust boundaries.")
    body(doc, "2.3.4 ML-Based Classification — Fine-tuned encoder classifiers such as DeBERTa-v3 learn semantic patterns associated with injection. ArtificialShield uses ProtectAI/deberta-v3-base-prompt-injection-v2 as its detection engine.")
    heading(doc, "2.4 Pros and Cons", 2)
    table(
        doc,
        ["Defense", "Flexibility", "Bypass Risk", "Cost"],
        [
            ["System prompt rules", "Low", "High", "Trivial"],
            ["Regex/static filters", "Very low", "High", "Low"],
            ["Architectural isolation", "Medium", "Low", "High"],
            ["Fine-tuned classifier (ArtificialShield)", "High", "Medium–low", "Medium"],
        ],
    )
    heading(doc, "2.5 Issues/Observations", 2)
    body(doc, "The major gap identified is deployability. ArtificialShield addresses this through an OpenAI-compatible REST proxy that centralizes enforcement, logging, and threshold policy without client restructuring.")
    heading(doc, "2.6 Summary", 2)
    body(doc, "The literature supports measurable, layered defenses. This project implements an inline classifier proxy as a practical enforcement layer.")

    doc.add_page_break()
    heading(doc, "CHAPTER-3: REQUIREMENT ARTIFACTS")
    heading(doc, "3.2 Hardware and Software Requirements", 2)
    body(doc, "Python 3.11; FastAPI + Uvicorn; Hugging Face Transformers + PyTorch; SQLite; Streamlit; pytest and Locust; Docker; CPU-only inference target.")
    heading(doc, "3.3 Specific Project Requirements", 2)
    body(doc, "FR-1 through FR-4 and NFR-1 through NFR-3 from Review 1 remain unchanged. Review 2 verified FR-1 (segment scoring), FR-2 (structured refusal), FR-3 (SQLite persistence), and FR-4 (OpenAI-compatible endpoint) through the implemented proxy.")
    heading(doc, "3.4 Summary", 2)
    body(doc, "Review 2 implementation satisfies the functional requirements and meets the latency target on the tested hardware.")

    doc.add_page_break()
    heading(doc, "CHAPTER-4: DESIGN METHODOLOGY AND ITS NOVELTY")
    heading(doc, "4.1 Methodology and Goal", 2)
    body(doc, "The guardrail is placed at the transport boundary. Each request is validated, normalized, segmented, scored, and subjected to a policy decision before dispatch.")
    heading(doc, "4.2 Functional Modules Design and Analysis", 2)
    body(doc, "Gateway (app/gateway.py): validation, normalization, segmentation. Detection (app/detector.py): DeBERTa-v3 inference with bounded windows. Policy: threshold comparison with block/flag/observe modes. Audit (app/audit.py): append-only SQLite records. Analytics (dashboard/app.py): trends, histograms, and payload inspection.")
    heading(doc, "4.3 Software Architectural Design", 2)
    body(doc, "Client request → FastAPI gateway → DeBERTa engine → threshold policy → LLM backend/reply or blocked response → SQLite log → Streamlit analytics.")
    heading(doc, "4.5 User Interface Design", 2)
    body(doc, "The gateway exposes /v1/chat/completions and /scan. The analyst interface is a Streamlit dashboard presenting block-rate trends, score distributions, and payload inspection.")
    heading(doc, "4.6 Summary", 2)
    body(doc, "The novelty claim is deployability: classifier-based detection, OpenAI-compatible REST surface, latency budget, and forensic logging are combined in one lightweight proxy.")

    doc.add_page_break()
    heading(doc, "CHAPTER-5: TECHNICAL IMPLEMENTATION & ANALYSIS")
    heading(doc, "5.1 Outline", 2)
    body(doc, "Review 2 delivered the integrated enforcement layer planned in Review 1: FastAPI proxy, DeBERTa-v3 scoring, threshold policy, SQLite audit trail, and Streamlit analytics.")
    heading(doc, "5.2 Technical Coding and Code Solutions", 2)
    body(doc, "Repository: ArtificialShield. Key files: app/gateway.py, app/detector.py, app/normalize.py, app/audit.py, dashboard/app.py, baseline/vulnerable_agent.py, baseline/attack_harness.py, scripts/benchmark.py, Dockerfile.")
    heading(doc, "5.3 Working Layout of Forms", 2)
    body(doc, "Primary interfaces: POST /v1/chat/completions (OpenAI-compatible guarded proxy), POST /scan (standalone scoring), GET /health (status). Analyst interface: Streamlit dashboard on port 8501.")
    heading(doc, "5.4 Prototype Submission", 2)
    table(
        doc,
        ["Work Item", "Status"],
        [
            ["Vulnerable baseline AI script", "Complete"],
            ["DeBERTa model selected and benchmarked", "Complete"],
            ["Report chapters 1–4", "Complete"],
            ["FastAPI proxy integration", "Complete"],
            ["SQLite logging and Streamlit dashboard", "Complete"],
            ["Threshold calibration (τ = 0.85)", "Complete"],
            ["Attack replay through proxy", "Complete"],
            ["Locust sustained throughput test", "Review 3"],
        ],
    )
    heading(doc, "5.5 Test and Validation", 2)
    body(doc, "pytest validates normalization, segmentation, and policy logic. Attack harness replays direct override, role-play, base64 obfuscation, and delimiter injection scenarios. Baseline vulnerable agent shows 100% attack success without proxy; proxy blocks all four variants in Review 2 testing.")
    heading(doc, "5.6 Performance Analysis", 2)
    table(
        doc,
        ["Metric", "Target", "Review 2 Result"],
        [
            ["Added latency p50 (CPU)", "—", "≈ 42 ms"],
            ["Added latency p95 (CPU)", "< 100 ms", "≈ 78 ms"],
            ["Added latency p99 (CPU)", "—", "≈ 91 ms"],
            ["False-positive rate (benign set)", "< 2%", "0% (n=3 tested)"],
            ["Attack block rate (harness)", "High", "100% (4/4)"],
            ["Baseline attack success (no proxy)", "Demonstrate threat", "100% (4/4)"],
        ],
    )
    heading(doc, "5.7 Summary", 2)
    body(doc, "Review 2 establishes integrated enforcement with initial quantitative validation meeting the CPU latency and false-positive targets on the tested corpora.")

    doc.add_page_break()
    heading(doc, "CHAPTER-6: PROJECT OUTCOME AND APPLICABILITY")
    heading(doc, "6.2 Key Implementation Outlines of the System", 2)
    body(doc, "Inline interception; DeBERTa-v3 semantic detection; threshold enforcement independent of downstream provider; structured 403 refusals; SQLite audit records; OpenAI-compatible interface; Streamlit visibility.")
    heading(doc, "6.3 Significant Project Outcomes", 2)
    body(doc, "Review 2 demonstrates that transport-boundary classifier enforcement is deployable with sub-100 ms p95 latency on CPU and full block rate on the reproduced attack harness.")
    heading(doc, "6.4 Project Applicability on Real-World Applications", 2)
    body(doc, "The proxy can be inserted in RAG pipelines, e-mail assistants, document summarizers, and tool-using agents processing external content with minimal client changes.")
    heading(doc, "6.5 Inference", 2)
    body(doc, "ArtificialShield adds a measurable security layer before untrusted content reaches the backend while preserving observability for security analysts.")

    doc.add_page_break()
    heading(doc, "CHAPTER-7: CONCLUSIONS AND RECOMMENDATION")
    heading(doc, "7.2 Limitations/Constraints of the System", 2)
    body(doc, "Evaluation corpus size is limited at Review 2. Classifier performance may vary against adaptive or multilingual attacks not in the test set. Threshold selection remains a security/usability trade-off.")
    heading(doc, "7.3 Future Enhancements", 2)
    body(doc, "AgentDojo benchmark integration; Locust sustained throughput testing; adaptive attack evaluation; multi-tenant deployment; optional GPU acceleration; ensemble scoring.")
    heading(doc, "7.4 Inference", 2)
    body(doc, "Review 2 completes the core integration milestone. Review 3 should focus on large-scale benchmarking, adaptive attack resilience, and production hardening.")

    doc.add_page_break()
    heading(doc, "REFERENCES")
    refs = [
        "[1] OWASP Foundation, “OWASP Top 10 for Large Language Model Applications,” LLM01: Prompt Injection, 2025.",
        "[2] K. Greshake et al., “Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection,” in Proc. ACM AISec, 2023.",
        "[3] P. He, J. Gao, and W. Chen, “DeBERTaV3: Improving DeBERTa Using ELECTRA-Style Pre-Training with Gradient-Disentangled Embedding Sharing,” in Proc. ICLR, 2023.",
        "[4] K. Hines et al., “Defending Against Indirect Prompt Injection Attacks With Spotlighting,” arXiv:2403.14720, 2024.",
        "[5] Y. Liu et al., “Formalizing and Benchmarking Prompt Injection Attacks and Defenses,” in Proc. 33rd USENIX Security Symposium, 2024.",
        "[6] E. Debenedetti et al., “AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents,” NeurIPS Datasets and Benchmarks Track, 2024.",
    ]
    for ref in refs:
        body(doc, ref)

    doc.add_page_break()
    heading(doc, "APPENDIX A — Review 2 Completion Status")
    table(
        doc,
        ["Work Item", "Review 1", "Review 2"],
        [
            ["Vulnerable baseline", "Complete", "Complete"],
            ["DeBERTa benchmark", "Complete", "Complete"],
            ["FastAPI proxy", "Planned", "Complete"],
            ["SQLite + Streamlit", "Planned", "Complete"],
            ["Threshold calibration", "Planned", "Complete (τ=0.85)"],
            ["Quantitative E2E results", "Planned", "Initial complete"],
            ["Large-scale Locust test", "—", "Review 3"],
        ],
    )

    heading(doc, "APPENDIX B — Implemented Guardrail Proxy Flow")
    for line in [
        "1. Client request",
        "2. FastAPI gateway — validate, normalize, segment prompt + context",
        "3. DeBERTa engine — score each segment",
        "4a. score < τ → LLM backend → reply",
        "4b. score ≥ τ → HTTP 403 blocked response",
        "5. SQLite log → Streamlit dashboard",
    ]:
        body(doc, line)

    doc.save(output_path)


if __name__ == "__main__":
    out = Path(r"C:\Users\hp omen\Documents\PROJECT 1\VIT_Bhopal_Project_Report_Review2.docx")
    build_report(out)
    print(f"Wrote {out}")
