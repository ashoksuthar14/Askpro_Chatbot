import os
import uuid
import json
from typing import Dict, List

from gemini_client import call_gemini


class Summarizer:
	def __init__(self):
		pass

	def _strip_code_fence(self, text: str) -> str:
		if not text:
			return ""
		clean = text.strip()
		if clean.startswith("```"):
			clean = clean.strip("`\n ")
			if "\n" in clean:
				clean = clean.split("\n", 1)[1]
		return clean

	def _render_html_bullets(self, key_points: List[str]) -> str:
		items = ''.join(f'<li>{p}</li>' for p in key_points[:3])
		return f"<div class=\"summary-card\"><h4>Summary</h4><ul>{items}</ul></div>"

	def _coerce_points(self, raw: Dict, text: str, sentences: int) -> Dict:
		key_points = raw.get("key_points")
		if isinstance(key_points, list):
			points = [p for p in key_points if isinstance(p, str) and p.strip()][:3]
		else:
			# Fallback: split by newline or periods
			tmp = (raw.get("summary") or text)
			parts = [p.strip(" -•\t\n") for p in tmp.split("\n") if p.strip()]
			if len(parts) < 3:
				parts = [s.strip() for s in tmp.split(".") if s.strip()]
			points = parts[:3]
		if len(points) < 3:
			# pad from text words if needed
			extra = " ".join(text.split()[:60])
			for _ in range(3 - len(points)):
				points.append(extra)
		html = self._render_html_bullets(points)
		return {"key_points": points[:3], "html": html}

	def _summarize_text(self, text: str) -> Dict:
		prompt = (
			"Summarize the following article as exactly 3 concise bullet points (no intro/outro).\n"
			"Return JSON: { \"key_points\": [\"point 1\", \"point 2\", \"point 3\"] }\n"
			f"Article:\n{text}"
		)
		resp = call_gemini(prompt)
		payload = self._strip_code_fence(resp.get("text", ""))
		try:
			parsed = json.loads(payload)
		except Exception:
			parsed = {"key_points": [] , "summary": payload}
		return self._coerce_points(parsed, text, 3)

	def summarize(self, text: str, sentences: int = 3) -> Dict:
		if len(text) < 4000:
			result = self._summarize_text(text)
			result["summary_id"] = uuid.uuid4().hex
			return result
		chunk_size = 3000
		chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
		partials: List[Dict] = [self._summarize_text(ch) for ch in chunks]
		# combine partial points and choose top 3
		combined = []
		for p in partials:
			combined.extend(p.get("key_points", []))
		result = {"key_points": combined[:3]}
		result["html"] = self._render_html_bullets(result["key_points"]) 
		result["summary_id"] = uuid.uuid4().hex
		return result
