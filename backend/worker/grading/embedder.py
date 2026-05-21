from sentence_transformers import SentenceTransformer
from core.config import supabase_admin

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embed_text(text: str) -> list[float]:
    return get_model().encode(text).tolist()

def find_similar(embedding: list[float], exclude_grade_id: str, threshold: float = 0.92) -> list[dict]:
    # Use Supabase RPC for vector similarity search
    result = supabase_admin.rpc("find_similar_answers", {
        "query_embedding": embedding,
        "similarity_threshold": threshold,
        "exclude_id": exclude_grade_id
    }).execute()
    return result.data or []
