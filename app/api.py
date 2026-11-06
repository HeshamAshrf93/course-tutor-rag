import os
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .ingest import load_pdf
from .retrieve import Retriever
from .tutor import GeminiClient, Tutor

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="Course Tutor RAG", version="0.1.0")


@lru_cache
def get_tutor() -> Tutor:
    chunks = []
    for pdf in sorted(Path(os.getenv("COURSE_DIR", ROOT / "course")).glob("*.pdf")):
        chunks.extend(load_pdf(pdf))
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return Tutor(Retriever(chunks), GeminiClient(key) if key else None)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class QuizRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=200)
    count: int = Field(default=3, ge=1, le=5)


@app.get("/health")
def health():
    return {"status": "ok", "chunks": len(get_tutor().retriever.chunks), "llm_enabled": get_tutor().llm is not None}


@app.post("/ask")
def ask(request: AskRequest):
    return get_tutor().ask(request.question).to_dict()


@app.post("/quiz")
def quiz(request: QuizRequest):
    return get_tutor().quiz(request.topic, request.count)


@app.get("/")
def index():
    return FileResponse(ROOT / "app" / "static" / "index.html")
