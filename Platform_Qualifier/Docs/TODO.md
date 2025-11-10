# Project TODO

- [ ] Add model selector in UI (choose Ollama model) and configurable top_k for RAG
- [ ] Cache embeddings per document to speed up repeated runs
- [ ] Add progress indicators/spinners for long LLM calls
- [ ] Add error banner if Ollama is unreachable, with troubleshooting tips
- [ ] Validate checklist sheet name and structure; show friendly message if missing
- [ ] Add unit tests for: checklist loader, score parsing, classification ranges
- [ ] Add pagination/expanders for long justifications in UI table
- [ ] Allow export to PDF in addition to Excel
- [ ] Batch processing for multiple documents (queue mode)
- [ ] Persist last run results with timestamp in a runs/ folder
- [ ] Add environment configuration (YAML) for endpoints and model name
- [ ] Add README quickstart and deployment guide
- [ ] CI: lint + basic tests workflow

## Done
- [x] Load checklist dynamically from Excel
- [x] Use local LLM (Ollama) with RAG
- [x] Parse Score (0–3) and Justification from model response
- [x] Compute weighted scores and total
- [x] Classify based on specified score ranges
- [x] Export results to Excel
- [x] Streamlit UI: upload, preview, results table, download
- [x] Robust document parsing for PDF/DOCX/TXT
