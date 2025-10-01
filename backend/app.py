import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any

from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from models import init_db, db_session
from memory_store import MemoryStore
from kb_manager import KBManager
from gemini_client import call_gemini, ensure_persona
from summarizer import Summarizer
from visualizer import Visualizer
from source_verifier import SourceVerifier
from rate_limiter import RateLimiter

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("askme-pro")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(BASE_DIR, "..", "uploads", "documents"))
DIAGRAM_FOLDER = os.getenv("DIAGRAM_FOLDER", os.path.join(BASE_DIR, "..", "uploads", "diagrams"))
MAX_PROMPT_CHARS = int(os.getenv("MAX_PROMPT_CHARS", "30000"))
MEMORY_MAX_TURNS = int(os.getenv("MEMORY_MAX_TURNS", "5"))
MEMORY_MAX_CHARS = int(os.getenv("MEMORY_MAX_CHARS", "2500"))
FAST_MODE = os.getenv("FAST_MODE", "1") == "1"  # Enables latency optimizations

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DIAGRAM_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "..", "frontend", "static"), template_folder=os.path.join(BASE_DIR, "..", "frontend", "templates"))
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["DIAGRAM_FOLDER"] = DIAGRAM_FOLDER

init_db()
memory_store = MemoryStore()
kb_manager = KBManager()
summarizer = Summarizer()
visualizer = Visualizer(output_dir=DIAGRAM_FOLDER)
source_verifier = SourceVerifier()
rate_limiter = RateLimiter(cooldown_seconds=1 if FAST_MODE else 2)


@app.teardown_appcontext
def shutdown_session(exception=None):
	db_session.remove()


@app.route("/")
def index():
	return render_template("index.html")


@app.route("/api/context/<session_id>", methods=["GET"]) 
def get_context(session_id: str):
	messages = memory_store.get_recent_messages(session_id, limit=MEMORY_MAX_TURNS)
	return jsonify({"session_id": session_id, "messages": messages})


@app.route("/api/upload", methods=["POST"]) 
def upload():
	if rate_limiter.is_limited(request):
		return jsonify({"error": "rate_limited"}), 429
	if "file" not in request.files:
		return jsonify({"error": "file_missing"}), 400
	file = request.files["file"]
	if file.filename == "":
		return jsonify({"error": "empty_filename"}), 400
	filename = secure_filename(file.filename)
	save_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex}_{filename}")
	file.save(save_path)
	# Ingest & index
	doc_id = kb_manager.ingest_document(save_path)
	return jsonify({"document_id": doc_id, "filename": filename})


@app.route("/api/summarize", methods=["POST"]) 
def summarize_endpoint():
	if rate_limiter.is_limited(request):
		return jsonify({"error": "rate_limited"}), 429
	payload = request.get_json(force=True)
	article_text = payload.get("text")
	doc_id = payload.get("document_id")
	if not article_text and not doc_id:
		return jsonify({"error": "no_input"}), 400
	if doc_id and not article_text:
		article_text = kb_manager.get_document_text(doc_id)
	try:
		result = summarizer.summarize(article_text)
		resp = {
			"key_points": result.get("key_points", [])[:3],
			"summary_id": result.get("summary_id", ""),
			"html": result.get("html", "")
		}
		return jsonify(resp)
	except Exception as e:
		logger.exception("summarize failed: %s", e)
		return jsonify({"error": "summarize_failed"}), 500


def build_prompt(question: str, mode: str, persona: str, context_chunks: list, memory_messages: list) -> str:
	persona_prefix = ""
	if persona and persona != "auto":
		persona_prefix = f"Persona: {persona}\n"
	system = (
		"You are AskMe Pro, an accurate, concise, and safe knowledge assistant. Always follow these rules:\n"
		"1) Respect the requested output mode (short, detailed, el5, deep_dive).\n"
		"2) If provided with `context:` (KB chunks or memory), prioritize and cite them. If you must use external knowledge, indicate \"SOURCE: <title> - <url>\".\n"
		"3) Where possible, include a small \"SOURCES\" section with URLs. If sources are not available, return honest uncertainty (\"I couldn't find a reliable source for this.\").\n"
		"4) Output MUST be valid JSON with keys: \"answer\", \"sources\" (list of {title,url,snippet}), \"action\" (optional), \"notes\" (optional).\n"
	)
	# Trim chunk text to reduce tokens
	def trim(t: str, n: int = 700) -> str:
		return (t[:n] + "…") if len(t) > n else t
	context_block = "\n".join([trim(c["text"]) for c in context_chunks]) if context_chunks else ""
	mem_lines = []
	for m in memory_messages:
		role = m.get("role")
		text = m.get("text")
		mem_lines.append(f"- {role}: \"{text}\"")
	memory_block = "\n".join(mem_lines)
	user = (
		f"USER QUESTION:\n{question}\n\n"
		f"MODE: {mode}\n"
		f"PERSONA: {persona}\n\n"
		f"CONTEXT (if any):\n{context_block}\n\n"
		f"MEMORY (last N messages):\n{memory_block}\n\n"
		"INSTRUCTIONS:\n"
		"1) Answer the USER QUESTION using CONTEXT and MEMORY primarily.\n"
		"2) Keep the answer length appropriate for MODE.\n"
		"3) If you reference facts from the CONTEXT, mark them inline with [source:CHUNK_ID] and also include full sources in the \"sources\" array.\n"
		"4) If the question requires a diagram, set \"action\":\"generate_diagram\" and provide a short diagram spec in \"notes\".\n\n"
		"Return machine-readable JSON only."
	)
	final_prompt = f"{persona_prefix}{system}\n\n{user}"
	return final_prompt[: (20000 if FAST_MODE else MAX_PROMPT_CHARS)]


@app.route("/api/chat", methods=["POST"]) 
def chat():
	if rate_limiter.is_limited(request):
		return jsonify({"error": "rate_limited"}), 429
	payload = request.get_json(force=True)
	session_id = payload.get("session_id") or uuid.uuid4().hex
	question = payload.get("question", "").strip()
	mode = payload.get("mode", "short")
	persona = payload.get("persona", "auto")
	article_id = payload.get("article_id")
	use_memory = bool(payload.get("use_memory", True))
	if not question:
		return jsonify({"error": "empty_question"}), 400
	# memory
	recent_memory = memory_store.get_recent_messages(session_id, limit=(3 if FAST_MODE else MEMORY_MAX_TURNS)) if use_memory else []
	# kb retrieval
	context_chunks = kb_manager.retrieve(question, top_k=(2 if FAST_MODE else 3))
	# persona auto
	if persona == "auto":
		persona = ensure_persona(question)
	prompt = build_prompt(question, mode, persona, context_chunks, recent_memory)
	# lower output tokens and temp in fast mode
	generation_overrides = {"max_output_tokens": 500, "temperature": 0.1} if FAST_MODE else {}
	model_resp = call_gemini(prompt, **generation_overrides) if generation_overrides else call_gemini(prompt)
	# parse
	def _safe_parse(text: str):
		try:
			clean = text.strip()
			if clean.startswith("```"):
				clean = clean.strip("`\n ")
				if "\n" in clean:
					clean = clean.split("\n", 1)[1]
			return json.loads(clean)
		except Exception:
			return {"answer": text, "sources": [], "action": "", "notes": ""}
	parsed = _safe_parse(model_resp.get("text", "")) if isinstance(model_resp, dict) else {"answer": str(model_resp)}
	answer = parsed.get("answer", "")
	sources = parsed.get("sources", [])
	action = parsed.get("action", "")
	notes = parsed.get("notes", "")
	# optionally skip slow source verification in fast mode
	all_sources = sources
	if not FAST_MODE:
		wiki_sources = source_verifier.verify(question)
		all_sources = sources + wiki_sources
	# memory append
	memory_store.add_message(session_id, role="user", text=question)
	memory_store.add_message(session_id, role="assistant", text=answer)
	resp = {
		"session_id": session_id,
		"answer": answer,
		"sources": all_sources,
		"used_kb_chunks": [c["id"] for c in context_chunks],
		"confidence": "medium",
	}
	# diagram generation path unchanged
	if action == "generate_diagram" and isinstance(notes, str) and notes:
		try:
			diagram_id = visualizer.generate_from_spec(notes)
			resp["diagram"] = f"/api/diagram/{diagram_id}"
		except Exception as e:
			logger.exception("diagram generation failed: %s", e)
	return jsonify(resp)


@app.route("/api/diagram/<path:diagram_id>", methods=["GET"]) 
def get_diagram(diagram_id: str):
	return send_from_directory(DIAGRAM_FOLDER, diagram_id)


if __name__ == "__main__":
	app.run()

