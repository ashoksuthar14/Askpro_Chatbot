# AskMe-Pro-Chatbot  

### [Visit the Website](https://askpro-chatbot-deployable.onrender.com/)  
---

## 📖 Introduction  
**AskMe Pro** is an AI-powered **knowledge companion chatbot** designed to provide intelligent, context-aware, and source-backed responses.  

By integrating **Google Gemini LLM, document retrieval, summarization, memory, and source verification**, AskMe Pro enables users to **chat naturally, summarize documents, and retrieve knowledge** seamlessly.  

The platform combines **advanced AI with an intuitive frontend** to deliver a production-ready prototype that is lightweight, efficient, and user-friendly.  

---

<img src="images/chat_ui.png" alt="AskMe Pro Chat Interface" />  

---

## ✨ Key Features  

### 1. **AI Chat with Modes & Personas** 🤖  
*Adaptive chatbot powered by Gemini*  
- Response modes: **short, detailed, EL5 (Explain Like I’m 5), deep_dive**  
- Personas: **teacher, coder, comedian, coach, auto-detect**  
- Context-aware answers with conversation memory  

<img src="images/chat_modes.png" alt="Chat Modes and Personas" />  

---

### 2. **Document Upload & Retrieval** 📂  
*Local Knowledge Base using TF-IDF*  
- Upload `.txt` or `.pdf` files  
- Indexed using **TF-IDF retrieval** (no external embeddings)  
- Context chunks are used in answers for grounded responses  

<img src="images/doc_upload.png" alt="Document Upload Interface" />  

---

### 3. **Summarization** 📑  
*Smart AI-powered summarizer*  
- Summarizes any article/document into **exactly 3 bullet points**  
- Outputs clean, concise summaries with HTML-styled cards  

<img src="images/summary.png" alt="3-Point Summarization" />  

---

### 4. **Conversation Memory** 🧠  
*Persistent, session-based memory system*  
- Stored in **SQLite with SQLAlchemy ORM**  
- Retrieves past messages for continuity  
- Enhances chatbot’s contextual awareness  

---

### 5. **Wikipedia Source Verification** 🌍  
*Quick fact-checking from trusted sources*  
- Integrates with the **Wikipedia API**  
- Provides **title, snippet, and URL** for relevant facts  
- Ensures transparency in AI responses  

---

### 6. **Diagram Generation** 📊  
*AI-assisted knowledge visualization*  
- Generates **knowledge diagrams** from text specs  
- Built using **NetworkX + Matplotlib**  
- Served as PNG images in chat  

---

### 7. **Rate Limiting** ⏱️  
*Protects against abuse and spamming*  
- Per-IP/session cooldowns  
- Adjustable via backend settings  

---

### 8. **Frontend Interface** 🎨  
*Clean and modern UI for smooth interactions*  
- Built with **HTML, CSS, and JavaScript**  
- Features **chat bubbles, file upload, and summarizer**  
- Voice input with **Web Speech API** (input only)  
- Styled with **glassmorphic theme**  

<img src="images/frontend.png" alt="Frontend UI" />  

---

## 🛠️ Technologies Used  

- **Frontend:** HTML, CSS, JavaScript, Web Speech API  
- **Backend:** Flask, SQLAlchemy, Gunicorn, Alembic  
- **AI Tools:** Google Gemini (`gemini-2.5-flash`), scikit-learn (TF-IDF), NLTK, Wikipedia API  
- **Visualization:** NetworkX, Matplotlib  
- **PDF/Text Parsing:** PyPDF2, pdfminer.six  
- **Database:** SQLite (local memory + document storage)  

---

## 🚀 How to Run the Project Locally  

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/askme-pro.git
   cd askme-pro


## Quickstart
1. Create `.env` from example and set `GEMINI_API_KEY`.
```bash
cp .env.example .env
```
2. Install dependencies and run server
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd backend
gunicorn app:app --chdir backend --bind 0.0.0.0:5000
```

3. Open http://localhost:5000
