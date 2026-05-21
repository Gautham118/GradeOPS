create extension if not exists vector;
-- The embedding column is already added in 004; this migration just ensures the extension exists
-- and creates the HNSW index for production (more accurate than IVFFlat for small datasets)
create index if not exists grades_embedding_hnsw
  on grades using hnsw (embedding vector_cosine_ops);
