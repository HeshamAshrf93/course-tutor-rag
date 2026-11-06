"""Hybrid retrieval: BM25 + character n-grams, with optional semantic embeddings."""
import math
from collections import Counter
from dataclasses import dataclass
from typing import Callable, Protocol, Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .ingest import Chunk
from .textnorm import expand_query, tokens


class Embedder(Protocol):
    def __call__(self, texts: Sequence[str]) -> np.ndarray: ...


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float
    coverage: float


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.4, b: float = 0.75):
        self.docs, self.k1, self.b = docs, k1, b
        self.tf = [Counter(d) for d in docs]
        self.len = [len(d) for d in docs]
        self.avg = sum(self.len) / max(len(docs), 1)
        df = Counter(t for d in docs for t in set(d))
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
        self.max_idf = math.log(1 + (n + 0.5) / 0.5)

    def scores(self, query: list[str]) -> np.ndarray:
        result = np.zeros(len(self.docs))
        for i, tf in enumerate(self.tf):
            norm = self.k1 * (1 - self.b + self.b * self.len[i] / self.avg)
            result[i] = sum(self.idf.get(t, 0) * tf[t] * (self.k1 + 1) / (tf[t] + norm) for t in query if t in tf)
        return result


def _rrf(rankings: list[np.ndarray], k: int = 60) -> np.ndarray:
    total = np.zeros(len(rankings[0]))
    for scores in rankings:
        order = np.argsort(-scores)
        for rank, index in enumerate(order):
            if scores[index] > 0:
                total[index] += 1 / (k + rank + 1)
    return total


class Retriever:
    def __init__(self, chunks: list[Chunk], embedder: Embedder | None = None):
        self.chunks, self.embedder = chunks, embedder
        self.texts = [f"{c.heading}. {c.text}" for c in chunks]
        self.doc_tokens = [tokens(t) for t in self.texts]
        self.bm25 = BM25(self.doc_tokens)
        self.chars = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), lowercase=True, sublinear_tf=True)
        self.char_matrix = self.chars.fit_transform(self.texts)
        self.vectors = None
        if embedder is not None:
            self.vectors = self._unit(np.asarray(embedder(self.texts), dtype=float))

    @staticmethod
    def _unit(matrix: np.ndarray) -> np.ndarray:
        return matrix / np.maximum(np.linalg.norm(matrix, axis=1, keepdims=True), 1e-12)

    def coverage(self, query_terms: list[str], doc: list[str]) -> float:
        terms = set(query_terms)
        if not terms:
            return 0.0
        present = set(doc)
        # Arabic words left after term mapping are often generic ("slow", "compare"), so they count less.
        weight = lambda t: self.bm25.idf.get(t, self.bm25.max_idf) * (1.0 if t.isascii() else 0.25)
        total = sum(weight(t) for t in terms)
        return sum(weight(t) for t in terms if t in present) / total

    def search(self, query: str, k: int = 5) -> list[Hit]:
        expanded = expand_query(query)
        terms = tokens(expanded)
        if not terms and self.vectors is None:
            return []
        rankings = [self.bm25.scores(terms)]
        rankings.append((self.char_matrix @ self.chars.transform([expanded]).T).toarray().ravel())
        if self.vectors is not None:
            query_vector = self._unit(np.asarray(self.embedder([query]), dtype=float))
            rankings.append((self.vectors @ query_vector.T).ravel().clip(min=0))
        fused = _rrf(rankings)
        coverages = np.array([self.coverage(terms, d) for d in self.doc_tokens])
        # Rerank: fused rank signal plus how much of the rare query vocabulary the chunk actually holds.
        pairs = list(zip(terms, terms[1:]))
        phrases = np.array([sum(pair in set(zip(d, d[1:])) for pair in pairs) for d in self.doc_tokens], dtype=float)
        final = fused * (1 + 2 * coverages + phrases)
        order = np.argsort(-final)[:k]
        return [Hit(self.chunks[i], float(final[i]), float(coverages[i])) for i in order if final[i] > 0]


def baseline_search(chunks: list[Chunk], tokenizer: Callable[[str], list[str]]):
    """Plain BM25 without Arabic handling; kept to measure what the improvements add."""
    bm25 = BM25([tokenizer(f"{c.heading}. {c.text}") for c in chunks])

    def search(query: str, k: int = 5) -> list[Chunk]:
        scores = bm25.scores(tokenizer(query))
        return [chunks[i] for i in np.argsort(-scores)[:k] if scores[i] > 0]

    return search
