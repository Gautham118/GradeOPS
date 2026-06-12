# backend/preload_model.py  (new file)
from sentence_transformers import SentenceTransformer
print("Downloading all-MiniLM-L6-v2...")
SentenceTransformer("all-MiniLM-L6-v2")
print("Done.")