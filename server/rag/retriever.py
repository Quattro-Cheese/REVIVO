from __future__ import annotations

import faiss
import pickle
import numpy as np
from pathlib import Path

RAG_DIR = Path(__file__).resolve().parent


class GuidelineRetriever:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        # 지연 로드: __init__ 에서 모델 로드 안 함
        self.model = None
        self.index = None
        self.chunks = None
        self._initialized = True

    def _load(self):
        """실제 요청 시 처음 한 번만 로드"""
        if self.model is not None:
            return
        from sentence_transformers import SentenceTransformer

        print("RAG 모델 로드 중...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = faiss.read_index(str(RAG_DIR / "guideline.index"))
        with open(RAG_DIR / "chunks.pkl", "rb") as f:
            self.chunks = pickle.load(f)
        print(f"✅ RAG 로드 완료: {len(self.chunks)}개 청크")

    def search(self, query: str, top_k: int = 3) -> list[str]:
        self._load()
        query_vec = self.model.encode([query]).astype("float32")
        _, indices = self.index.search(query_vec, top_k)
        return [self.chunks[i] for i in indices[0] if i < len(self.chunks)]
