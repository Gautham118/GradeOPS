from sentence_transformers import SentenceTransformer
from core.config import supabase_admin

model = SentenceTransformer("all-MiniLM-L6-v2")  # 384-dim, loads once

def embed_and_store(grade_id: str, question_id: str, transcription: str):
    """Generate embedding for transcription and store in grades table."""
    embedding = model.encode(transcription).tolist()

    supabase_admin.table("grades")\
        .update({"embedding": embedding})\
        .eq("id", grade_id)\
        .execute()

    return embedding


def check_plagiarism(
    grade_id: str,
    question_id: str,
    embedding: list[float],
    threshold: float = 0.85
) -> bool:
    """
    Query pgvector for similar answers to the same question.
    Returns True if any other submission exceeds the similarity threshold.
    """
    # Raw SQL via Supabase RPC for vector similarity search
    result = supabase_admin.rpc(
        "find_similar_answers",
        {
            "query_embedding": embedding,
            "question_id_input": question_id,
            "exclude_grade_id": grade_id,
            "similarity_threshold": threshold
        }
    ).execute()

    print(f"[PLAG] grade={grade_id}")
    print(f"[PLAG] question={question_id}")
    print(f"[PLAG] matches={len(result.data)}")
    print(f"[PLAG] data={result.data}")

    return len(result.data) > 0
