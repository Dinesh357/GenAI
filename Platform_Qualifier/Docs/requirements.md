# Platform Qualifier Tool – Requirements Document

## 1. **Introduction**
The Platform Qualifier Tool is designed to automate the evaluation of customer-provided RFPs, PRDs, and BRDs to determine whether a project qualifies as a platform-specific initiative or a simple application. The tool leverages local LLMs for privacy and integrates with a scoring system based on a predefined Platform Qualification Checklist.

---

## 2. **Objectives**
- Reduce manual effort for pre-sales teams in evaluating platform traits.
- Ensure data privacy by using self-hosted LLMs (e.g., Ollama, llama.cpp).
- Provide an interactive interface for document upload and automated scoring.
- Generate classification reports based on weighted scores.

---

## 3. **Scope**
- Input: RFP, PRD, BRD documents in PDF, DOCX, TXT formats.
- Output: Classification as **Application Development**, **Modular Product**, **Emerging Platform**, or **Enterprise-grade Platform**.
- Integration with local LLM for question answering and justification.
- Export results to Excel or PDF.

---

## 4. **Functional Requirements**
### 4.1 Document Ingestion
- Support file upload for PDF, DOCX, TXT.
- Extract text using PyMuPDF and python-docx.

### 4.2 Checklist Evaluation
- Load checklist dynamically from Excel file.
- For each question:
  - Query local LLM with context and question.
  - Parse response for **Score (0–3)** and **Justification**.

### 4.3 Scoring Engine
- Compute weighted scores using formula: `Weighted Score = Score × Weight`.
- Aggregate total score.
- Classify project based on predefined ranges:
  - 0–300 → Application Development
  - 301–600 → Modular Product
  - 601–850 → Emerging Platform
  - >850 → Enterprise-grade Platform

### 4.4 User Interface
- Streamlit-based UI:
  - Upload document.
  - Display extracted text preview.
  - Show checklist evaluation table with scores and justifications.
  - Display total score and classification.
  - Download results as Excel.

### 4.5 LLM Integration
- Use Ollama or llama.cpp for local inference.
- Prompt template:
  ```
  Context: <document text>
  Question: <checklist question>
  Respond with:
  Score: <0-3>
  Justification: <brief explanation>
  ```

---

## 5. **Non-Functional Requirements**
- **Privacy**: No data sent to external APIs.
- **Performance**: Response time per question ≤ 3 seconds.
- **Scalability**: Support documents up to 50 pages.
- **Usability**: Simple UI for non-technical users.

---

## 6. **Technology Stack**
- **Frontend**: Streamlit
- **Backend**: Python (FastAPI optional for API layer)
- **LLM Engine**: Ollama or llama.cpp
- **Document Parsing**: PyMuPDF, python-docx
- **Data Handling**: Pandas
- **Storage**: Local file system (Excel outputs)

---

## 7. **Deliverables**
- Streamlit application with integrated LLM scoring.
- Python modules:
  - `document_parser.py`
  - `local_llm_interface.py`
  - `scoring.py`
- Sample Excel checklist.
- Deployment guide.

---

## 8. **Future Enhancements**
- Fine-tune local LLM with historical RFPs.
- Add multi-document batch processing.
- Include dashboard for analytics and trends.
