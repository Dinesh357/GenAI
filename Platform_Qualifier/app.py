import streamlit as st
import pandas as pd
from modules.document_parser import parse_document, chunk_text, RAGRetriever
from modules.checklist_loader import load_checklist
from modules.llm_interface import evaluate_checklist_with_rag
from modules.scoring_engine import compute_weighted_scores
from modules.classification import classify_project
from modules.excel_writer import generate_result_excel

st.title("Platform Qualification Tool")

uploaded_file = st.file_uploader("Upload RFP/PRD/BRD Document", type=["pdf", "docx", "txt"])

if uploaded_file:
    # Step 1: Parse document
    raw_text = parse_document(uploaded_file)
    st.subheader("Extracted Text")
    st.text_area("Document Preview", raw_text[:3000], height=300)

    # Avoid re-running heavy analysis on every Streamlit rerun
    if "analysis" not in st.session_state:
        st.session_state.analysis = None
        st.session_state.last_filename = None

    # Run analysis only when explicitly triggered
    st.subheader("LLM Analysis")
    run = st.button("Run analysis")

    # Reset cached analysis if a different file is uploaded
    current_name = getattr(uploaded_file, "name", None)
    if st.session_state.last_filename != current_name:
        st.session_state.analysis = None
        st.session_state.last_filename = current_name

    if run or st.session_state.analysis is not None:
        if st.session_state.analysis is None:
            print(f"[App] Analysis triggered file={current_name} text_chars={len(raw_text)}", flush=True)
            # Step 2: Chunk text
            chunks = chunk_text(raw_text)

            # Step 3: Initialize RAG retriever (embeddings computed here)
            retriever = RAGRetriever(chunks)
            print("[App] Retriever ready", flush=True)

            # Step 4: Load checklist items
            try:
                items = load_checklist()
                print(f"[App] Checklist items loaded: {len(items)}", flush=True)
            except Exception as e:
                print(f"[App] Checklist load failed: {e}", flush=True)
                st.error(f"Checklist load failed: {e}")
                items = []

            # Step 5: Evaluate each checklist item via LLM with RAG
            if items:
                print(f"[App] Starting evaluation for {len(items)} items", flush=True)
                eval_results = evaluate_checklist_with_rag(retriever, items)
            else:
                eval_results = {}

            # Step 6: Compute weighted scores
            rows, total = compute_weighted_scores(items, eval_results)

            # Step 7: Classify project based on total
            category = classify_project(total)
            print(f"[App] Evaluation complete rows={len(rows)} total={total:.2f} category={category}", flush=True)

            st.session_state.analysis = {
                "rows": rows,
                "total": total,
                "category": category,
            }

        # Step 8: Display results from cache
        rows = st.session_state.analysis["rows"]
        total = st.session_state.analysis["total"]
        category = st.session_state.analysis["category"]

        st.subheader("Checklist Evaluation Results")
        df = pd.DataFrame(rows)
        st.dataframe(df)
        st.metric("Total Weighted Score", f"{total:.0f}")
        st.success(f"Project classified as: {category}")

        # Step 9: Generate Excel output and provide download
        out_path = generate_result_excel(rows, total, category)
        with open(out_path, "rb") as f:
            st.download_button(
                label="Download Result Excel",
                data=f.read(),
                file_name="Platform_Qualification_Result.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
