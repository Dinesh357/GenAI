
import fitz  # PyMuPDF
import docx
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

# Parse text from different file types
def parse_document(file):
    if file.name.endswith('.pdf'):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = "".join([page.get_text() for page in doc])
    elif file.name.endswith('.docx'):
        doc = docx.Document(file)
        text = "".join([para.text for para in doc.paragraphs])
    elif file.name.endswith('.txt'):
        text = file.read().decode("utf-8")
    else:
        text = "Unsupported file format"
    return text

# Chunk text into smaller segments
def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

# Simplified RAG Retriever using cosine similarity
class RAGRetriever:
    def __init__(self, chunks):
        self.chunks = chunks
        self.embeddings = model.encode(chunks)

    def retrieve(self, query, top_k=3):
        query_embedding = model.encode([query])[0].reshape(1, -1)
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [self.chunks[i] for i in top_indices]
