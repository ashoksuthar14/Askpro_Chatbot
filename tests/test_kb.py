import os
import tempfile
from backend.kb_manager import KBManager


def test_chunk_and_retrieve():
	kb = KBManager(chunk_size=50, chunk_overlap=10)
	text = "Python is a programming language. It is widely used for AI and ML. Flask is a micro web framework for Python."
	with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt') as f:
		f.write(text)
		path = f.name
	try:
		doc_id = kb.ingest_document(path)
		res = kb.retrieve('What is Flask?', top_k=2)
		assert any('Flask' in r['text'] for r in res)
	finally:
		os.remove(path)
