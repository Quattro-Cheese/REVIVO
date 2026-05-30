# server/rag/build_index.py
# 처음 한 번만 실행

import faiss
import pickle
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

RAG_DIR = Path(__file__).resolve().parent


def load_pdf_chunks(path: Path, chunk_size: int = 300) -> list[str]:
    try:
        import PyPDF2

        chunks = []
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if not text:
                    continue
                # 페이지를 chunk_size 단위로 분리
                text = text.strip()
                for i in range(0, len(text), chunk_size):
                    chunk = text[i : i + chunk_size].strip()
                    if len(chunk) > 30:  # 너무 짧은 청크 제외
                        chunks.append(chunk)
        return chunks
    except ImportError:
        raise ImportError("PyPDF2 설치 필요: pip install PyPDF2")


# PDF 로드
pdf_path = RAG_DIR / "aha_guidelines.pdf"
print(f"PDF 로드 중: {pdf_path}")
chunks = load_pdf_chunks(pdf_path)
print(f"청크 수: {len(chunks)}")

if not chunks:
    print("❌ PDF에서 텍스트를 추출하지 못했습니다.")
    exit(1)

# 샘플 출력
for i, c in enumerate(chunks[:3]):
    print(f"[{i}] {c[:80]}...")

# 임베딩 생성
print("\n임베딩 생성 중... (첫 실행 시 모델 다운로드 ~80MB)")
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks, show_progress_bar=True)

# FAISS 인덱스 저장
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings).astype("float32"))

faiss.write_index(index, str(RAG_DIR / "guideline.index"))
with open(RAG_DIR / "chunks.pkl", "wb") as f:
    pickle.dump(chunks, f)

print(f"\n✅ 인덱스 저장 완료: {len(chunks)}개 청크")
