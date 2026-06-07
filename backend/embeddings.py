from sentence_transformers import SentenceTransformer
import numpy as np

_model = None


def load_embedding_model():
    global _model
    print("Loading Sentence-BERT (all-MiniLM-L6-v2)...")
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Sentence-BERT loaded.")


def embed_sentences(sentences: list[str]) -> np.ndarray:
    if _model is None:
        raise RuntimeError("Embedding model not loaded. Call load_embedding_model() first.")

    embeddings = _model.encode(sentences, convert_to_numpy=True)
    return embeddings