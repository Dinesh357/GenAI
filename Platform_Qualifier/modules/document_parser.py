
import fitz  # PyMuPDF
import docx
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from io import BytesIO
import time

model = SentenceTransformer('all-MiniLM-L6-v2')

# Parse text from different file types
def parse_document(file):
    start = time.perf_counter()
    name = getattr(file, 'name', '') or ''
    if name.endswith('.pdf'):
        data = file.read()
        doc = fitz.open(stream=data, filetype="pdf")
        text = "".join([page.get_text() for page in doc])
    elif name.endswith('.docx'):
        # Ensure we read bytes and wrap in BytesIO
        data = file.read()
        doc = docx.Document(BytesIO(data))
        text = "".join([para.text for para in doc.paragraphs])
    elif name.endswith('.txt'):
        data = file.read()
        try:
            text = data.decode("utf-8")
        except Exception:
            text = data.decode("latin-1", errors='ignore')
    else:
        text = "Unsupported file format"
    elapsed = time.perf_counter() - start
    print(f"[Parse] file={name} chars={len(text)} elapsed={elapsed:.2f}s", flush=True)
    return text

# Chunk text into smaller segments
def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    print(f"[Chunks] words={len(words)} chunk_size={chunk_size} chunks={len(chunks)}", flush=True)
    return chunks

# Simplified RAG Retriever using cosine similarity
class RAGRetriever:
    def __init__(self, chunks):
        self.chunks = chunks
        start = time.perf_counter()
        self.embeddings = model.encode(chunks, batch_size=16, convert_to_numpy=True)
        elapsed = time.perf_counter() - start
        device = getattr(model, 'device', 'unknown')
        print(f"[Embeddings] chunks={len(chunks)} batch_size=16 device={device} elapsed={elapsed:.2f}s", flush=True)

    def retrieve(self, query, top_k=3):
        print(f"[Retrieve] top_k={top_k} query_chars={len(query)}", flush=True)
        query_embedding = model.encode([query], convert_to_numpy=True)[0].reshape(1, -1)
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [self.chunks[i] for i in top_indices]
