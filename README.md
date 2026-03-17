# ⚖️ Law Chatbot — AI Based Indian Legal Guidance System

An AI-powered legal chatbot that provides **first-level legal awareness** to common users. Ask any legal question in plain everyday language and get a **structured response** with the applicable **LAW, SECTION, PUNISHMENT, NEXT STEPS, and DISCLAIMER** — instantly.

---

## 🎯 Key Features

- **Plain Language Input** — Type legal questions in simple English; no legal jargon needed
- **Typo & Slang Handling** — Fixes 80+ common misspellings and expands informal phrases
- **Structured Responses** — Every answer follows a consistent LAW → SECTION → PUNISHMENT → NEXT STEPS → DISCLAIMER format
- **55+ Quick Questions** — One-click buttons for common legal queries (FIR filing, cyber complaint, helpline numbers, etc.)
- **RAG Pipeline** — Retrieval Augmented Generation using ChromaDB vector search + keyword fallback
- **Async Processing** — Celery + Redis handle heavy AI tasks in the background; UI stays fast
- **Local AI** — Ollama runs the LLM and embeddings locally; no data sent to external cloud services
- **Safety First** — Every response includes a legal disclaimer; fallback guidance when confidence is low

---

## 🏗️ Architecture — APRM Pipeline

```
User Query
    │
    ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  A — Analyze    │────▶│  P — Process    │────▶│  R — Retrieve   │────▶│  M — Model      │
│                 │     │                 │     │                 │     │                 │
│ Query Under-    │     │ Django REST API │     │ ChromaDB Vector │     │ Ollama LLM      │
│ standing, Typo  │     │ Celery + Redis  │     │ Search, Keyword │     │ Strict Prompt   │
│ Fix, Intent     │     │ Async Dispatch  │     │ Fallback, Fuzzy │     │ Fallback Chain  │
│ Detection       │     │                 │     │ Matching        │     │ Structured Out  │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
                                                                              │
                                                                              ▼
                                                                    Structured Legal Response
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite 5, Tailwind CSS 3, Axios |
| **Backend** | Django 5.1, Django REST Framework, Python 3.11 |
| **Async** | Celery (task queue), Redis 7 (message broker) |
| **AI / RAG** | Ollama (llama3.2:3b), LangChain, ChromaDB, nomic-embed-text |
| **Database** | SQLite3 (chat sessions & queries) |
| **Vector Store** | ChromaDB (persistent, `indian_law_collection`) |
| **Data** | Pandas, difflib (fuzzy matching) |
| **Deployment** | Docker & Docker Compose |

---

## 📁 Project Structure

```
law-chatbot/
├── docker-compose.yml          # 5 services: redis, ollama, backend, celery, frontend
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── manage.py
│   ├── requirements.txt
│   ├── db.sqlite3              # SQLite database
│   ├── core/
│   │   ├── settings.py         # Django + Celery + Ollama config
│   │   ├── urls.py             # Root URL routing
│   │   ├── celery.py           # Celery app setup
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── chat/
│   │   ├── models.py           # ChatSession, LegalQuery models
│   │   ├── views.py            # API views (create session, submit query, poll messages, catalog)
│   │   ├── urls.py             # Chat API endpoints
│   │   ├── serializers.py      # DRF serializers
│   │   ├── tasks.py            # Celery task: process_legal_query (APRM pipeline)
│   │   ├── rag_setup.py        # ChromaDB setup, vector search, synonym groups
│   │   ├── query_understanding.py  # Typo fix, intent detection, phrase expansion
│   │   ├── simple_qa.py        # Quick FAQ answers + default guidance
│   │   └── management/commands/
│   │       ├── import_law_assets.py
│   │       └── rebuild_legal_kb.py
│   ├── chroma_db/              # Persistent ChromaDB vector storage
│   └── data/
│       └── legal_sections.csv  # Legal knowledge base (law, section, punishment, next_steps, keywords)
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── index.html
    └── src/
        ├── App.jsx             # Main chat interface
        ├── main.jsx
        └── index.css
```

---

## 🚀 Getting Started

### Prerequisites

- **Docker** & **Docker Compose** installed
- At least **8 GB RAM** (Ollama LLM needs memory)
- Ports `3000`, `8000`, `6379`, `11434` available

### Quick Start (Docker Compose)

```bash
# Clone the repository
git clone <repo-url>
cd law-chatbot

# Start all services
docker-compose up --build

# Pull the required Ollama models (run once, in a separate terminal)
docker exec -it <ollama-container-name> ollama pull llama3.2:3b
docker exec -it <ollama-container-name> ollama pull nomic-embed-text
```

The app will be available at:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api/chat/

### Manual Setup (Without Docker)

#### 1. Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Start Redis (must be running)
redis-server

# Start Ollama (must be running with models pulled)
ollama serve
ollama pull llama3.2:3b
ollama pull nomic-embed-text

# Initialize RAG knowledge base + run migrations
python chat/rag_setup.py
python manage.py migrate

# Start Django server
python manage.py runserver 0.0.0.0:8000

# Start Celery worker (separate terminal)
celery -A core worker -l info
```

#### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat/sessions/` | Create a new chat session |
| `POST` | `/api/chat/query/` | Submit a legal query (returns 202, dispatches async task) |
| `GET` | `/api/chat/<session_id>/` | Poll session messages (used for real-time updates) |
| `GET` | `/api/chat/catalog/?search=` | Search the legal knowledge base catalog |

### Example: Submit a Query

```bash
# Create session
curl -X POST http://localhost:8000/api/chat/sessions/

# Submit query
curl -X POST http://localhost:8000/api/chat/query/ \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1, "user_query": "someone stole my bike"}'

# Poll for response
curl http://localhost:8000/api/chat/1/
```

---

## ⚙️ Configuration

Key settings in `backend/core/settings.py`:

| Variable | Default | Description |
|---|---|---|
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Redis broker URL |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/1` | Celery result backend |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3.2:3b` | LLM model for response generation |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model for vector search |
| `RAG_DATA_PATH` | `data/legal_sections.csv` | Legal knowledge base file |
| `CHROMA_PERSIST_DIR` | `chroma_db/` | ChromaDB persistent storage directory |

---

## 🔄 Processing Pipeline

1. **Simple QA Check** — Handles greetings, FIR filing steps, emergency helpline numbers instantly without AI
2. **Query Understanding** — Fixes typos (80+ corrections), expands informal phrases, detects legal intent (30+ categories), extracts entities
3. **Best Entry Lookup** — Token overlap (70%) + fuzzy matching (30%) scoring; if confidence ≥ 0.42, returns direct answer
4. **RAG Retrieval** — ChromaDB semantic similarity search returns top-3 matching legal sections
5. **LLM Generation** — Ollama generates structured response with strict prompt enforcement
6. **Fallback Chain** — Three-level fallback: entry-based → context-based → default guidance
7. **Safety Disclaimer** — Every response includes mandatory legal consultation advice

---

## 📊 Data Source

The knowledge base (`data/legal_sections.csv`) contains Indian legal sections with columns:

| Column | Description |
|---|---|
| `law` | Name of the act (IPC, IT Act, BNSS, Motor Vehicles Act, etc.) |
| `section` | Specific section number and title |
| `punishment` | Penalties and imprisonment details |
| `next_steps` | Recommended actions for the user |
| `keywords` | Search keywords for matching |

---

## 🐳 Docker Services

| Service | Image | Port | Purpose |
|---|---|---|---|
| `redis` | `redis:7-alpine` | 6379 | Message broker for Celery |
| `ollama` | `ollama/ollama:latest` | 11434 | Local LLM + embeddings |
| `backend` | Custom (Python 3.11) | 8000 | Django REST API server |
| `celery` | Same as backend | — | Async task worker |
| `frontend` | Custom (Node 20) | 3000 | React Vite dev server |

---

## 🔮 Future Scope

- **Multilingual Support** — Tamil, Hindi, and other Indian languages
- **Voice Input** — Speech-to-text for accessibility
- **Mobile App** — React Native or Flutter client
- **Expanded Legal Data** — More acts, recent amendments, state-specific laws
- **User Authentication** — Save chat history across sessions
- **Analytics Dashboard** — Track common queries and usage patterns

---

## ⚠️ Disclaimer

This chatbot provides **first-level legal awareness only**. It is **NOT a substitute for professional legal advice**. Always consult a qualified lawyer for final legal decisions.

---

## 📄 License

This project is developed for academic/educational purposes.
