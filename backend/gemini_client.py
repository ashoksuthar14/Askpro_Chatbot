import os
import json
import logging
from typing import Dict, Any

import requests

logger = logging.getLogger(__name__)

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Paste your Gemini API key below to hardcode it. Leave empty to use environment variable GEMINI_API_KEY.
HARDCODED_API_KEY = "AIzaSyDBjgg0egV4Noiam1cJHNEq8bO4c3Q4J-4"  # <-- PASTE YOUR KEY HERE (e.g., "AIza...")

# Optional file fallback: place your key in backend/gemini_key.txt (single line)
_KEY_FILE_PATH = os.path.join(os.path.dirname(__file__), "gemini_key.txt")
_FILE_KEY = ""
try:
	if os.path.exists(_KEY_FILE_PATH):
		with open(_KEY_FILE_PATH, "r", encoding="utf-8") as fh:
			_FILE_KEY = fh.read().strip()
except Exception:
	_FILE_KEY = ""

API_KEY = HARDCODED_API_KEY or _FILE_KEY or os.getenv("GEMINI_API_KEY", "")
GEMINI_MOCK = os.getenv("GEMINI_MOCK", "0") == "1"
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "800"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))

_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": "AskMePro/1.0", "Connection": "keep-alive"})


def _mock_response(prompt: str) -> Dict[str, Any]:
	return {
		"text": json.dumps({
			"answer": "This is a mocked response for testing.",
			"sources": [],
			"action": "",
			"notes": ""
		})
	}


def ensure_persona(question: str) -> str:
	q = question.lower()
	if any(k in q for k in ["code", "compile", "bug", "function"]):
		return "coder"
	if any(k in q for k in ["train", "exercise", "workout", "practice"]):
		return "coach"
	if any(k in q for k in ["exam", "explain", "learn", "study"]):
		return "teacher"
	return "teacher"


def call_gemini(prompt: str, model: str = MODEL_NAME, temperature: float = TEMPERATURE, max_output_tokens: int = MAX_OUTPUT_TOKENS) -> Dict[str, Any]:
	if GEMINI_MOCK:
		return _mock_response(prompt)
	if not API_KEY:
		raise RuntimeError("GEMINI_API_KEY not configured. Set HARDCODED_API_KEY, create backend/gemini_key.txt, or export GEMINI_API_KEY.")
	# Prefer REST for lower overhead
	try:
		endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
		payload = {
			"contents": [{"parts": [{"text": prompt}]}],
			"generationConfig": {"temperature": temperature, "maxOutputTokens": max_output_tokens, "candidateCount": 1}
		}
		r = _SESSION.post(endpoint, json=payload, timeout=20)
		r.raise_for_status()
		data = r.json()
		text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
		if text:
			return {"text": text}
	except Exception as e:
		logger.warning("Gemini REST failed, trying SDK: %s", e)
	# Fallback to SDK
	try:
		import google.generativeai as genai
		genai.configure(api_key=API_KEY)
		model_obj = genai.GenerativeModel(model)
		resp = model_obj.generate_content(prompt, generation_config={"temperature": temperature, "max_output_tokens": max_output_tokens, "candidate_count": 1})
		text = getattr(resp, "text", None) or (resp.candidates[0].content.parts[0].text if getattr(resp, "candidates", None) else "")
		return {"text": text}
	except Exception as e:
		logger.error("Gemini SDK also failed: %s", e)
		return {"text": json.dumps({"answer": "(error contacting Gemini)", "sources": []})}
