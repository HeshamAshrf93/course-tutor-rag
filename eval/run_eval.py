"""Measures retrieval and refusal behaviour. Run: python -m eval.run_eval"""
import json
import sys
from pathlib import Path

from app.ingest import load_pdf
from app.retrieve import Retriever, baseline_search
from app.textnorm import raw_tokens
from app.tutor import Tutor
from eval.questions import DEV, TEST

CHUNKS = load_pdf(Path(__file__).resolve().parent.parent / "course" / "data_structures_notes.pdf")


def rank_metrics(rows, search):
    answerable = [(q, p) for q, p in rows if p is not None]
    hit1 = hit3 = rr = 0.0
    misses = []
    for q, page in answerable:
        pages = [c.page for c in search(q)]
        rank = pages.index(page) + 1 if page in pages else None
        hit1 += rank == 1
        hit3 += bool(rank and rank <= 3)
        rr += 1 / rank if rank else 0
        if rank != 1:
            misses.append({"q": q, "expected": page, "got": pages[:3]})
    n = len(answerable)
    return {"hit@1": round(hit1 / n, 3), "hit@3": round(hit3 / n, 3), "mrr": round(rr / n, 3), "n": n}, misses


def refusal_metrics(rows, retriever, threshold):
    tutor = Tutor(retriever, min_coverage=threshold)
    tp = fp = fn = tn = 0
    errors = []
    for q, page in rows:
        answered = tutor.is_answerable(retriever.search(q), q)
        if page is None and not answered: tn += 1
        elif page is None: fp += 1; errors.append({"q": q, "error": "answered_off_topic"})
        elif answered: tp += 1
        else: fn += 1; errors.append({"q": q, "error": "wrong_refusal"})
    off, on = tn + fp, tp + fn
    return {"correct_refusals": f"{tn}/{off}", "wrong_refusals": f"{fn}/{on}"}, errors


def main():
    retriever = Retriever(CHUNKS)
    base = baseline_search(CHUNKS, raw_tokens)
    hybrid = lambda q: [h.chunk for h in retriever.search(q)]
    best_t, best = None, -1
    for t in [x / 100 for x in range(30, 91, 5)]:
        tutor = Tutor(retriever, min_coverage=t)
        score = sum(tutor.is_answerable(retriever.search(q), q) == (p is not None) for q, p in DEV)
        if score >= best:  # Ties go to the stricter threshold.
            best_t, best = t, score
    report = {"threshold_from_dev": best_t}
    for name, rows in (("dev", DEV), ("test", TEST)):
        b, _ = rank_metrics(rows, base)
        h, misses = rank_metrics(rows, hybrid)
        ref, errors = refusal_metrics(rows, retriever, best_t)
        report[name] = {"baseline_bm25": b, "hybrid": h, "refusal": ref, "misses": misses, "refusal_errors": errors}
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    out = Path(__file__).parent / "results.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
