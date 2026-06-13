from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import exams, submissions, grades

app = FastAPI(title="GradeOps API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://gradeops.vercel.app",   # ← add this (your Vercel URL)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exams.router,       prefix="/exams",       tags=["exams"])
app.include_router(submissions.router, prefix="/submissions",  tags=["submissions"])
app.include_router(grades.router,      prefix="/grades",       tags=["grades"])

@app.get("/health")
def health():
    return {"status": "ok"}