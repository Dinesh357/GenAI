import streamlit as st
from modules.document_parser import parse_document, chunk_text, RAGRetriever
from modules.llm_interface import answer_questions_with_rag
from modules.scoring_engine import compute_scores
from modules.classification import classify_project
from modules.excel_writer import generate_output_excel

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

    # Step 4: Retrieve relevant chunks for each prompt
    st.subheader("LLM Analysis")
    answers = answer_questions_with_rag(retriever)
    
    # Step 5: Score answers
    scores = compute_scores(answers)

    # Step 6: Classify project
    category = classify_project(scores)

    # Step 7: Generate Excel output
    generate_output_excel(answers, scores, category)

    st.success(f"Project classified as: {category}")
    st.download_button("Download Result Excel", "data/Platform_Qualification_Result.xlsx")
