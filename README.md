# Course Tutor RAG

An AI tutor that answers students only from their course material. It cites the source page and declines when the course doesn't cover the question.

## The problem

Many Arabic-speaking CS students study from English notes but think through questions in Arabic. General chatbots answer anyway, even when the answer isn't in their course. This project keeps answers tied to the material, so a student can check every one.

## What it does

- Takes questions in English, Arabic, or Egyptian Arabic, and searches English course PDFs
- Returns the source file and page with each answer
- Declines off-topic questions instead of guessing
- Creates fill-in-the-blank review questions from the material
- Runs without an API key in citation-only mode; adding a Gemini key turns on written explanations

## How it works

```
Course PDF -> page-aware chunks
Question -> Arabic normalization and course-term mapping
         -> BM25 + character n-grams (optional embeddings)
         -> Reciprocal Rank Fusion -> rerank by term coverage and phrases
         -> coverage check -> answer with citations, or decline
```

With Gemini on, an answer with no valid citation is discarded and replaced by a direct quote from the course.

## Evaluation

The questions and labels are in `eval/questions.py`. Run `python -m eval.run_eval`. Full output: `eval/results.json`.

| Metric | Plain BM25 (test) | This system (test) | This system (dev) |
|---|---|---|---|
| Correct page first (Hit@1) | 61.9% | 100% (21/21) | 91.3% (21/23) |
| Correct page in top 3 (Hit@3) | 61.9% | 100% (21/21) | 95.7% (22/23) |
| Off-topic questions declined | not measured | 9/9 | 8/8 |
| Valid questions wrongly declined | not measured | 1/21 | 0/23 |

**How to read these numbers:** the test set is small, I wrote it myself, and the course is an 8-page sample. Its score was also rerun after a bug fix found while trying a comparison question. Treat this as a regression check, not proof of real-world accuracy. Real student questions would be the next test.

Only retrieval and refusal were measured. Gemini answer quality has not been evaluated, so RAGAS is the next step.

## Known limitations

- Arabic search depends on a hand-written term list. Unlisted spellings, such as "المرج سورت", can be wrongly declined.
- Abbreviations that aren't in the course, such as "BST", can be wrongly declined.
- A question mixing a course term with an outside topic, such as "البحث في جوجل", can get an irrelevant answer without Gemini.
- "How does binary search work?" in Arabic can rank the binary search tree page first.
- Without Gemini, Arabic questions get a quote in English.
- Scanned PDFs need OCR first. Arabic PDFs haven't been tested.
- The optional embeddings path has only been tested with a fake embedder.
- The API has no login or rate limiting yet, so add both before a public launch.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
uvicorn app.api:app --reload
```

Open http://localhost:8000. To enable Gemini, copy `.env.example` to `.env`, set your key, and load it into your environment. Never commit `.env`.

To use your own course, put text-based PDFs in `course/`, and only use material you have the right to use. The included notes are original samples.

### Docker

```bash
docker build -t course-tutor .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key course-tutor
```

The Docker image hasn't been build-tested yet.

## Stack

Python, FastAPI, scikit-learn, pypdf, Gemini API (optional), pytest, Docker
