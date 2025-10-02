AskMe-Pro-Chatbot
Visit the Website
📖 Introduction

AskMe Pro is an AI-powered knowledge companion chatbot designed to provide intelligent, context-aware, and source-backed responses.

By integrating Google Gemini LLM, document retrieval, summarization, memory, and source verification, AskMe Pro enables users to chat naturally, summarize documents, and retrieve knowledge seamlessly.

The platform combines advanced AI with an intuitive frontend to deliver a production-ready prototype that is lightweight, efficient, and user-friendly.

<img src="images/chat_ui.png" alt="AskMe Pro Chat Interface" />
✨ Key Features
1. AI Chat with Modes & Personas 🤖

Adaptive chatbot powered by Gemini

Response modes: short, detailed, EL5 (Explain Like I’m 5), deep_dive

Personas: teacher, coder, comedian, coach, auto-detect

Context-aware answers with conversation memory

<img src="images/chat_modes.png" alt="Chat Modes and Personas" />
2. Document Upload & Retrieval 📂

Local Knowledge Base using TF-IDF

Upload .txt or .pdf files

Indexed using TF-IDF retrieval (no external embeddings)

Context chunks are used in answers for grounded responses

<img src="images/doc_upload.png" alt="Document Upload Interface" />
3. Summarization 📑

Smart AI-powered summarizer

Summarizes any article/document into exactly 3 bullet points

Outputs clean, concise summaries with HTML-styled cards

<img src="images/summary.png" alt="3-Point Summarization" />
4. Conversation Memory 🧠

Persistent, session-based memory system

Stored in SQLite with SQLAlchemy ORM

Retrieves past messages for continuity

Enhances chatbot’s contextual awareness

5. Wikipedia Source Verification 🌍

Quick fact-checking from trusted sources

Integrates with the Wikipedia API

Provides title, snippet, and URL for relevant facts

Ensures transparency in AI responses

6. Diagram Generation 📊

AI-assisted knowledge visualization

Generates knowledge diagrams from text specs

Built using NetworkX + Matplotlib

Served as PNG images in chat

7. Rate Limiting ⏱️

Protects against abuse and spamming

Per-IP/session cooldowns

Adjustable via backend settings

8. Frontend Interface 🎨

Clean and modern UI for smooth interactions

Built with HTML, CSS, and JavaScript

Features chat bubbles, file upload, and summarizer

Voice input with Web Speech API (input only)

Styled with glassmorphic theme

<img src="images/frontend.png" alt="Frontend UI" />
🛠️ Technologies Used

Frontend: HTML, CSS, JavaScript, Web Speech API

Backend: Flask, SQLAlchemy, Gunicorn, Alembic

AI Tools: Google Gemini (gemini-2.5-flash), scikit-learn (TF-IDF), NLTK, Wikipedia API

Visualization: NetworkX, Matplotlib

PDF/Text Parsing: PyPDF2, pdfminer.six

Database: SQLite (local memory + document storage)

🚀 How to Run the Project Locally

Clone the repository:

git clone https://github.com/your-username/askme-pro.git
cd askme-pro


Create and activate a virtual environment:

python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate


Install dependencies:

pip install -r backend/requirements.txt


Set up environment variables:

cp .env.example .env
# Add your GEMINI_API_KEY and other configs


Run the Flask backend:

cd backend
flask --app app run


Open http://localhost:5000
 in your browser

📂 Project Structure
askme-pro/
├── backend/                 # Flask backend & APIs
│   ├── app.py               # Main Flask app
│   ├── gemini_client.py     # Gemini API integration
│   ├── kb_manager.py        # TF-IDF retrieval system
│   ├── summarizer.py        # 3-point summarization
│   ├── memory_store.py      # SQLite conversation memory
│   ├── source_verifier.py   # Wikipedia source check
│   ├── visualizer.py        # Diagram generator
│   ├── models.py            # DB models (SQLAlchemy)
│   └── rate_limiter.py      # IP/session rate limiting
├── frontend/                # UI files
│   ├── templates/index.html # Chat UI template
│   ├── static/app.js        # Frontend logic
│   ├── static/styles.css    # Styling
└── tests/                   # Pytest unit tests

⚙️ Environment Variables

Create a .env file in the backend directory with the following:

GEMINI_API_KEY=your_gemini_api_key
FAST_MODE=1
DATABASE_URL=sqlite:///askme_pro.db
UPLOAD_FOLDER=uploads/documents
DIAGRAM_FOLDER=uploads/diagrams

🔧 Future Improvements

Real-time typing indicators

Better mobile responsiveness

Enhanced status feedback for uploads & summaries

Replace TF-IDF with semantic embeddings (FAISS, Sentence Transformers)

Multi-document knowledge base search

Long-term memory with vector databases

Image support (OCR + Gemini Vision)

Advanced diagram interactivity

Deployment on Render/Vercel with persistent DB

User authentication & accounts
