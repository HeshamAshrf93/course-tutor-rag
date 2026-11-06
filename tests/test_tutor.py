import httpx
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.api import app
from app.ingest import Chunk, chunk_page
from app.retrieve import Retriever
from app.textnorm import expand_query, normalize
from app.tutor import GeminiClient, Tutor

CHUNKS = [
    Chunk(0, "n.pdf", 1, "Stacks", "A stack is a Last In, First Out structure. Push adds an item to the top."),
    Chunk(1, "n.pdf", 2, "Queues", "A queue is a First In, First Out structure. Enqueue adds an item at the rear."),
    Chunk(2, "n.pdf", 3, "Hash Tables", "A collision happens when two keys map to the same index."),
]


def fake_llm(reply=None, error=False):
    def handler(request):
        if error:
            return httpx.Response(500)
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": reply}]}}]})
    return GeminiClient("test", "m", transport=httpx.MockTransport(handler))


@pytest.fixture
def retriever():
    return Retriever(CHUNKS)


def test_arabic_normalization_and_expansion():
    assert normalize("أحمد") == "احمد"
    assert "stack" in expand_query("ايه هو الستاك؟")


def test_arabic_question_finds_english_source(retriever):
    assert retriever.search("ايه هو الستاك؟")[0].chunk.page == 1


def test_refuses_off_topic_in_both_languages(retriever):
    tutor = Tutor(retriever)
    assert not tutor.ask("What is the capital of France?").grounded
    answer = tutor.ask("ايه عاصمة مصر؟")
    assert not answer.grounded and "مش موجودة" in answer.answer


def test_comparison_across_topics_is_answered_with_both_pages(retriever):
    answer = Tutor(retriever).ask("ايه الفرق بين الستاك والكيو؟")
    assert answer.grounded and {c.page for c in answer.citations} == {1, 2}


def test_extractive_answer_has_citation(retriever):
    answer = Tutor(retriever).ask("What is a queue?")
    assert answer.grounded and answer.mode == "extractive" and answer.citations[0].page == 2


def test_llm_answer_maps_citation_to_page(retriever):
    answer = Tutor(retriever, fake_llm("A queue is FIFO [1].")).ask("What is a queue?")
    assert answer.mode == "llm" and answer.citations[0].page == 2


def test_llm_uncited_or_failed_falls_back(retriever):
    for llm in (fake_llm("A queue is FIFO."), fake_llm(error=True)):
        answer = Tutor(retriever, llm).ask("What is a queue?")
        assert answer.mode == "extractive_fallback" and answer.citations


def test_llm_not_in_course_refuses(retriever):
    assert not Tutor(retriever, fake_llm("NOT_IN_COURSE")).ask("What is a queue?").grounded


def test_invented_citation_number_is_ignored(retriever):
    answer = Tutor(retriever, fake_llm("A queue is FIFO [9].")).ask("What is a queue?")
    assert answer.mode == "extractive_fallback"


def test_optional_embedder_path(retriever):
    def embedder(texts):
        return np.array([[1.0, float("stack" in t.lower() or "ستاك" in t)] for t in texts])
    assert Retriever(CHUNKS, embedder).search("ايه هو الستاك؟")[0].chunk.page == 1


def test_chunk_page_keeps_heading():
    heading, chunks = chunk_page("Title Here\nFirst sentence. Second sentence.")
    assert heading == "Title Here" and "First sentence." in chunks[0]


def test_quiz_is_grounded(retriever):
    result = Tutor(retriever).quiz("collision", seed=1)
    assert result["questions"] and "_____" in result["questions"][0]["question"]
    assert result["questions"][0]["answer"] in result["questions"][0]["options"]


def test_api_validates_and_answers():
    client = TestClient(app)
    assert client.post("/ask", json={"question": ""}).status_code == 422
    assert client.post("/ask", json={"question": "x" * 501}).status_code == 422
    assert client.post("/ask", json={"question": "What does LIFO mean?"}).json()["citations"][0]["page"] == 4
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/").status_code == 200
