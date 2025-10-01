import os
import json
import tempfile
import importlib

os.environ['GEMINI_MOCK'] = '1'

from backend.app import app, kb_manager


def test_upload_and_chat():
	client = app.test_client()
	# upload
	with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt') as f:
		f.write('Cats are small domesticated carnivorous mammals. They like to sleep.')
		path = f.name
	with open(path, 'rb') as fh:
		r = client.post('/api/upload', data={'file': (fh, 'cats.txt')})
		assert r.status_code == 200
		doc_id = r.get_json()['document_id']
	# chat
	payload = { 'question': 'What are cats?', 'mode': 'short', 'persona': 'auto', 'article_id': doc_id }
	r = client.post('/api/chat', data=json.dumps(payload), content_type='application/json')
	assert r.status_code == 200
	data = r.get_json()
	assert 'answer' in data
	assert 'session_id' in data
