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

    # Step 2: Chunk text
    chunks = chunk_text(raw_text)

    # Step 3: Initialize RAG retriever
    retriever = RAGRetriever(chunks)

    # Step 4: Load checklist items
    items = load_checklist()

    # Step 5: Evaluate each checklist item via LLM with RAG
    st.subheader("LLM Analysis")
    eval_results = evaluate_checklist_with_rag(retriever, items)

    # Step 6: Compute weighted scores
    rows, total = compute_weighted_scores(items, eval_results)

    # Step 7: Classify project based on total
    category = classify_project(total)

    # Step 8: Display results
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
