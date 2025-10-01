import os
import uuid
import re
from typing import List, Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from joblib import dump, load

from models import db_session, Document, Chunk

try:
	from PyPDF2 import PdfReader
except Exception:
	PdfReader = None


class KBManager:
	def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
		self.chunk_size = chunk_size or int(os.getenv("KB_CHUNK_SIZE", "1000"))
		self.chunk_overlap = chunk_overlap or int(os.getenv("KB_CHUNK_OVERLAP", "200"))
		self.vectorizer = None
		self.tfidf = None
		self.corpus_chunks: List[str] = []
		self.chunk_ids: List[str] = []
		self._loaded_from_db = False

	def _extract_text(self, path: str) -> str:
		if path.lower().endswith(".pdf") and PdfReader is not None:
			reader = PdfReader(path)
			text = "\n".join(page.extract_text() or "" for page in reader.pages)
			return text
		with open(path, "r", encoding="utf-8", errors="ignore") as f:
			return f.read()

	def _normalize(self, text: str) -> str:
		text = re.sub(r"\s+", " ", text or " ").strip()
		return text

	def _chunk(self, text: str) -> List[str]:
		text = self._normalize(text)
		chunks = []
		step = self.chunk_size - self.chunk_overlap
		for i in range(0, max(1, len(text)), step):
			chunk = text[i:i + self.chunk_size]
			if chunk:
				chunks.append(chunk)
		return chunks

	def ingest_document(self, path: str) -> str:
		text = self._extract_text(path)
		doc_id = uuid.uuid4().hex
		doc = Document(id=doc_id, title=os.path.basename(path), path=path, text=text)
		db_session.add(doc)
		db_session.commit()
		chunks = self._chunk(text)
		for idx, ch in enumerate(chunks):
			cid = f"{doc_id}_c{idx}"
			chunk = Chunk(id=cid, document_id=doc_id, text=ch, start=idx * (self.chunk_size - self.chunk_overlap), end=idx * (self.chunk_size - self.chunk_overlap) + len(ch))
			db_session.add(chunk)
			self.corpus_chunks.append(ch)
			self.chunk_ids.append(cid)
		db_session.commit()
		self._reindex()
		self._loaded_from_db = True
		return doc_id

	def _reindex(self) -> None:
		if not self.corpus_chunks:
			self.vectorizer = None
			self.tfidf = None
			return
		self.vectorizer = TfidfVectorizer(stop_words="english")
		self.tfidf = self.vectorizer.fit_transform(self.corpus_chunks)

	def get_document_text(self, document_id: str) -> str:
		doc = db_session.get(Document, document_id)
		return doc.text if doc else ""

	def _lazy_load(self) -> None:
		if self._loaded_from_db:
			return
		chunks = db_session.query(Chunk).all()
		self.corpus_chunks = [c.text for c in chunks]
		self.chunk_ids = [c.id for c in chunks]
		self._reindex()
		self._loaded_from_db = True

	def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
		self._lazy_load()
		if not self.corpus_chunks or not self.vectorizer or self.tfidf is None:
			return []
		q_vec = self.vectorizer.transform([query])
		sims = cosine_similarity(q_vec, self.tfidf)[0]
		idxs = sims.argsort()[::-1][:top_k]
		results = []
		for i in idxs:
			results.append({"id": self.chunk_ids[i], "text": self.corpus_chunks[i], "score": float(sims[i])})
		return results
