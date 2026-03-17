# ⚖️ Law Chatbot — Full Project Explanation (Tanglish)

> Indha file-la project-oda A to Z explanation irukku — architecture, APRM pipeline, RAG system, every module, every function, data flow, frontend, backend, Docker — ellamey Tanglish-la.

---

## 📌 1. Project Enna?

Indha project oru **AI-powered legal chatbot**. India-la irukura common people-ku basic legal awareness kodukura system idhu.

**Problem:** Normal ah oru aalu-ku bike thirudhu pona, salary varaala, harassment face panna — enna law apply aagum, enna section, enna punishment, enna steps edukanum nu theriyaadhu. Lawyer-kitta poradhuku time, money ellam selavu.

**Solution:** Indha chatbot-la user simple English-la type panniduvanga — "someone stole my bike" or "salary not paid" — system automatically correct law, section, punishment, next steps, disclaimer kudukum structured format-la.

**Key point:** User legal terminology therinja avasiyam illa. Spelling mistake panna kuda (like "sallary", "harrasment") system auto-correct panni correct answer kudukum.

---

## 📌 2. Technology Stack — Enna Enna Use Pannirukkom

| Component | Technology | Enna Pannum |
|---|---|---|
| **Frontend** | React 18 + Vite 5 + Tailwind CSS | Chat UI — user question type pannum, answer kaatum |
| **Backend** | Django 5.1 + Django REST Framework | API server — session create, query process, messages return |
| **Task Queue** | Celery + Redis | Heavy AI work-a background-la run pannum, UI block aagaadhu |
| **AI Model** | Ollama (llama3.2:3b) | Local LLM — structured legal answer generate pannum |
| **Embeddings** | Ollama (nomic-embed-text) | Text-a vector-a maathum, similar legal sections find pannum |
| **Vector DB** | ChromaDB | Legal sections-oda embeddings store pannum, similarity search pannum |
| **Database** | SQLite3 | Chat sessions, user questions, AI responses store pannum |
| **Data** | Pandas, difflib | CSV load pannum, fuzzy matching pannum |
| **Deploy** | Docker + Docker Compose | Ellam oru command-la start pannum (5 services) |

---

## 📌 3. APRM Architecture — Heart of the Project

APRM nu oru pipeline — user question vandhu final answer pogum varaikkum 4 step irukku. Idhudhan project-oda core architecture.

```
User Question
     │
     ▼
 ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
 │ ANALYZE  │───▶│ PROCESS │───▶│ RETRIEVE│───▶│  MODEL  │
 │          │    │         │    │         │    │         │
 │ Query    │    │ Django  │    │ ChromaDB│    │ Ollama  │
 │ Under-   │    │ API +   │    │ Vector  │    │ LLM +   │
 │ standing │    │ Celery  │    │ Search  │    │ Fallback│
 └─────────┘    └─────────┘    └─────────┘    └─────────┘
                                                    │
                                                    ▼
                                            Structured Answer
                                     (LAW / SECTION / PUNISHMENT
                                      / NEXT STEPS / DISCLAIMER)
```

### A — Analyze (Query Understanding)

**File:** `chat/query_understanding.py`

User type panna raw text-a eduthu clean pannum. Idhu first step.

**Enna enna pannum:**

1. **Lowercase + Clean** — "SOMEONE STOLE My Bike!!!" → "someone stole my bike"

2. **Typo Correction** — 80+ common misspellings fix pannum:
   - "sallary" → "salary"
   - "harrasment" → "harassment"
   - "marraige" → "marriage"
   - "badtouch" → "bad touch"
   - "rapped" → "rape"
   - "hosipital" → "hospital"

3. **Phrase Alias Expansion** — Informal phrases-a proper legal terms-a maathum (75+ rules):
   - "no road in my street" → "no road civic infrastructure street grievance"
   - "eb issue" → "electricity board complaint"
   - "bad touch" → "inappropriate touch sexual harassment"
   - "salary not paid" → "unpaid wages salary"

4. **Intent Detection** — 37 legal categories detect pannum:
   - `theft`, `murder`, `harassment`, `sexual_offence`, `cyber_fraud`
   - `privacy_violation`, `fire_arson`, `wage_dispute`, `domestic_violence`
   - `marriage_divorce`, `education_fee`, `hospital_issue`, `transport_bus`
   - `rto_transport`, `accident_traffic`, `traffic_rules`, `chain_snatching`
   - `tree_cutting`, `fake_doctor_medicine`, `women_safety`, `men_safety`
   - `child_elder_safety`, `trai_telecom`, `loan_banking`, `family_property`
   - `landlord_tenant`, `pollution`, `political_issues`, `local_governance`
   - `missing_person`, `temple_issues`, `civic_infra`, `land_property`
   - `agriculture`, `governance_rti`, `electricity_eb`, `advertising_grievance`

   **Epdi detect pannum?** — Query-la irukura words-a unigram (single word), bigram (2 words), trigram (3 words) ah check pannum each intent category keywords-oda.

5. **Entity Extraction** — Location (home, office, school), Time (today, night, morning), Objects (bike, phone, salary) extract pannum.

6. **Enriched Query Build** — Normalized query + detected intents + extracted entities ellam combine panni oru rich query string create pannum.

**Example:**
```
Input:  "sallary not payed since 3 months"
After:  normalized = "salary not paid since 3 months"
        intents = ["wage_dispute"]
        entities = ["salary"]
        enriched = "salary not paid since 3 months wage_dispute salary"
```

**Return:** `QueryUnderstanding` dataclass — `normalized_query`, `intents`, `entities`, `enriched_query`

---

### P — Process (API + Async)

**Files:** `chat/views.py`, `chat/tasks.py`, `core/celery.py`

Frontend-lirundu request varum, backend aatha handle panni Celery worker-ku dispatch pannum.

**Step by step:**

1. **User Submit pannum** → React frontend `POST /api/chat/query/` call pannum with `session_id` + `user_query`.

2. **Django View (SubmitQueryView):**
   - `CreateLegalQuerySerializer` use panni validate pannum (session_id valid ah, user_query irukka nu check pannum).
   - `LegalQuery` record create pannum database-la, status = `"pending"`.
   - `process_legal_query.delay(legal_query.id)` — Celery task fire pannum.
   - Immediately HTTP **202 Accepted** return pannum. User-ku loading indicator kaatum.

3. **Celery Worker picks up the task** — Background-la run aagum. Frontend block aagaadhu.

4. **Frontend polls** — Every 2 seconds `GET /api/chat/{session_id}/` call panni status check pannum. Status `"completed"` aana udan answer display pannum.

**Yenda async?** — Ollama LLM call panra, ChromaDB search panra — ellam heavy computation. Directly view-la panna user 10-30 seconds hang aagum. Athanaala Celery use panni background-la run pannrom.

**Celery Configuration:**
```python
# core/celery.py
app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()  # auto-ah chat/tasks.py-la irukura @shared_task find pannum
```

**Redis** — Celery-oda message broker. Task queue maintain pannum. Backend task dispatch panna Redis-la store aagum, Celery worker aatha pick up pannum.

---

### R — Retrieve (RAG System)

**File:** `chat/rag_setup.py` (1156 lines — project-oda biggest file)

Indha module-dhan project-oda brain. User question-ku matching law sections find pannum.

#### RAG Enna?

**RAG = Retrieval Augmented Generation**

Simple-a sonna: LLM-ku answer generate panra munnaadi, relevant legal information "retrieve" (find) panrom knowledge base-lirundu. Apdhi retrieve panna data-va LLM-ku context-a kodupom. LLM adha vachu better answer generate pannum.

**Without RAG:** LLM thaniyaa answer pannum → wrong or general answer varum.
**With RAG:** First related laws find panrom → adha LLM-ku kodupom → accurate structured answer varum.

#### Knowledge Base — legal_sections.csv

```
| law              | section         | punishment           | next_steps           | keywords        |
|------------------|-----------------|----------------------|----------------------|-----------------|
| IPC              | Section 378     | 3 years jail + fine  | 1. File FIR 2. ...   | theft, stolen   |
| IPC              | Section 302     | Death / life prison  | 1. File FIR 2. ...   | murder, killed  |
| IT Act           | Section 66D     | 3 years + fine       | 1. Cyber complaint   | online fraud    |
| Payment of Wages | Section 4       | Fine up to 7500     | 1. Labour court ...  | salary, wages   |
```

Indha CSV-la Indian laws irukku — IPC, IT Act, BNSS, Motor Vehicles Act, etc. Each row-la law name, section, punishment, next steps, keywords ellam irukku.

#### Vector Store — ChromaDB

1. **CSV load** pannum using Pandas.
2. **Keywords enrich** pannum — 50+ enrichment rules. Example: "theft" irundha "stolen, robbery, pickpocket, snatch" add pannum keywords-la.
3. **Each row-a text document-a convert** pannum: `"LAW: IPC\nSECTION: 378 Theft\nPUNISHMENT: ...\nNEXT STEPS: ..."`
4. **Ollama nomic-embed-text model** use panni text-a **vector (numbers list)** ah maathum.
5. **ChromaDB-la store** pannum. Persistent storage — restart panna kuda data irukum.

#### Search — Epdi Matching Law Find Pannum?

**3 strategy irukku:**

**Strategy 1: Curated Entry Lookup** (`_find_curated_complaint_entry`)
- 80+ if-block rules irukku.
- Specific phrases-ku exact legal mapping. Example:
  - "chain snatching" → IPC Section 356 (Snatching)
  - "fake doctor" → IPC Section 270 (Medical Negligence)
  - "tree cutting" → Indian Forest Act Section 33
  - "garbage not collected" → Municipal Corporation Act
  - "drunk driving" → Motor Vehicles Act Section 185
- Idhu match aana directly answer kudukum, no LLM needed.

**Strategy 2: Scored Search** (`find_best_legal_entry` + `_entry_score`)
- Every law entry-ku score calculate pannum:
  - **70% weight** — Token overlap (user query words vs entry keywords, how many match)
  - **30% weight** — Fuzzy string similarity (overall string matching using `difflib.SequenceMatcher`)
  - **Bonus points** — Exact section name match, domain-specific boosting
  - **Domain boosters** — harassment, arson, cyber, tax, telecom, road, land, caste, constitution topics-ku specific weight adjustments

- **Confidence ≥ 0.42** → Direct answer kudukum (LLM call panna vendaam)
- **Confidence < 0.42** → RAG vector search-ku pogum

**Strategy 3: Vector Similarity Search** (`get_context`)
- ChromaDB `similarity_search(query, k=3)` call pannum.
- User query-a vector-a maathi, stored law vectors-oda compare pannum.
- **Top 3 most similar** documents return pannum as context.
- **Fallback:** Ollama embeddings available illana `_keyword_fallback` run aagum (pure token-based matching).

#### Synonym Expansion

45+ synonym groups irukku. User "stolen" sonna system "theft, robbery, snatch, pickpocket, missing" ellam search pannum.

```python
SYNONYM_GROUPS = [
    {'theft', 'stolen', 'steal', 'robbery', 'snatch', 'pickpocket'},
    {'murder', 'killed', 'homicide', 'stabbing', 'shooting'},
    {'harassment', 'abuse', 'misbehave', 'molest', 'eve teasing'},
    {'fire', 'arson', 'burn', 'blaze', 'set fire'},
    ...
]
```

#### Phrase Normalization

130+ phrase mappings. Informal language-a formal legal terms-a maathum:

```python
PHRASE_NORMALIZATION = {
    'salary not paid': 'unpaid wages salary',
    'bike stolen': 'theft motorcycle vehicle',
    'someone hit me': 'assault physical violence',
    ...
}
```

---

### M — Model (LLM Response Generation)

**File:** `chat/tasks.py`

RAG-lirundu vandha context + user query-a Ollama LLM-ku anuppi structured answer generate pannum.

#### System Prompt

```
You are Indian Law Expert. Answer EXACTLY:
LAW: IPC 378
SECTION: Theft
PUNISHMENT: 3 years jail + fine
NEXT STEPS: 1.FIR 2.Evidence 3.Followup
DISCLAIMER: Consult lawyer

Use ONLY RAG context. No context = 'Consult lawyer'
```

Strict instructions — LLM always idhe format-la dhan answer pannum. Free-form long answer kudukkaadhu.

#### Prompt Building — `build_prompt()`

```python
def build_prompt(user_query, context):
    return f"""
    {SYSTEM_PROMPT}

    Strict output format:
    LAW: ...
    SECTION: ...
    PUNISHMENT: ...
    NEXT STEPS: 1... 2... 3...
    DISCLAIMER: Consult lawyer

    CONTEXT:
    {context}

    USER QUERY: {user_query}
    """
```

Context irukka → full prompt build pannum.
Context illa → "Return exactly: DISCLAIMER: Consult lawyer" nu sollidum.

#### Ollama API Call — `ask_ollama()`

```python
def ask_ollama(prompt):
    # Step 1: Health check — GET /api/tags (timeout 1.2s)
    # Step 2: POST /api/generate with model='llama3.2:3b', stream=False (timeout 45s)
    # Step 3: Return response text
```

- **llama3.2:3b** model use panrom — small but effective.
- **Locally runs** — no cloud, no internet needed, privacy safe.
- **45 second timeout** — slow response-ku wait pannum.

#### Three-Level Fallback Chain

LLM fail aanaalum system crash aagaadhu. 3 level fallback irukku:

```
Level 1: format_response_from_entry(entry)
         ↓ entry illana
Level 2: format_response_from_context(context)
         ↓ context illana
Level 3: get_default_guidance_response(query)
         → Generic legal guidance + "rephrase your question" message
```

**Eppavum answer varum** — LLM down aanaalum, ChromaDB empty aanaalum, system always oru useful response kudukum.

---

## 📌 4. Complete Task Pipeline — `process_legal_query()`

Idhu **Celery task** — background-la run aagum. Full pipeline order:

```
Step 1: Simple QA Check
        ├── "hi" / "hello" → greeting response
        ├── "how to file FIR" → FIR steps
        ├── "police number" → 100/112
        ├── "women helpline" → 181/1091
        └── Match aana → DONE (no AI needed)
                │
                ▼ (no match)
Step 2: Query Understanding (ANALYZE)
        ├── Typo correction (80+ fixes)
        ├── Phrase expansion (75+ aliases)
        ├── Intent detection (37 categories)
        ├── Entity extraction
        └── enriched_query build
                │
                ▼
Step 3: Best Entry Lookup
        ├── Curated entry check (80+ exact rules)
        ├── Scored search (token overlap + fuzzy)
        └── Confidence ≥ 0.42 → Direct answer → DONE
                │
                ▼ (confidence < 0.42)
Step 4: RAG Vector Search (RETRIEVE)
        ├── ChromaDB similarity_search(k=3)
        ├── Fallback: keyword-based search
        └── No context at all → default guidance → DONE
                │
                ▼ (got context)
Step 5: LLM Generation (MODEL)
        ├── build_prompt(query, context)
        ├── ask_ollama(prompt) → structured response
        ├── LLM fail → fallback to entry/context formatting
        └── Empty/bad response → fallback formatting
                │
                ▼
Step 6: Save Response
        ├── ai_response = final answer
        ├── status = 'completed'
        └── save to database
```

---

## 📌 5. Simple QA Module

**File:** `chat/simple_qa.py`

Basic questions-ku AI use pannama directly answer kudukum. Fast response.

**56 quick-question suggestions irukku:**
- "Hi", "What can you do?"
- "How to file FIR?", "Cyber complaint website?"
- "Police emergency number?", "Women helpline number?"
- "No road in my street", "Drainage overflow near my house"
- "Chain snatching happened", "Fake doctor treatment"
- "Drunk driving fine?", "How to get driving licence?"
- "Property tax not paid", "Crop loss compensation"
- etc.

**Functions:**

| Function | Enna Pannum |
|---|---|
| `get_simple_qa_response(query)` | Greetings, FIR steps, helpline numbers, basic FAQ match panna answer return pannum. Match aagala na `None` return pannum. |
| `get_default_guidance_response(query)` | Last resort fallback — generic guidance + "rephrase your question" message |

**Response format same:** LAW / SECTION / PUNISHMENT / NEXT STEPS / DISCLAIMER.

---

## 📌 6. Database Models

**File:** `chat/models.py`

**2 models dhan irukku — simple and clean:**

### ChatSession
```
- id          → auto primary key
- created_at  → session create aana time (auto)
```
Oru user chat-a start panna oru session create aagum. Multiple questions same session-la kekkalam.

### LegalQuery
```
- id          → auto primary key
- session     → ForeignKey to ChatSession (which session-la ketta question)
- status      → "pending" or "completed"
- user_query  → user ketta question text
- ai_response → AI generate panna answer (initially null)
- created_at  → question submit panna time
- updated_at  → answer complete aana time
```

**Flow:**
1. User question submit → `LegalQuery` create aagum with `status="pending"`, `ai_response=null`
2. Celery task complete → `status="completed"`, `ai_response` fill aagum
3. Frontend poll pannum → `status=="completed"` paarum → answer display pannum

---

## 📌 7. API Endpoints

**Files:** `chat/urls.py`, `chat/views.py`, `chat/serializers.py`

### 4 API Endpoints:

| Endpoint | Method | View | Enna Pannum |
|---|---|---|---|
| `/api/chat/sessions/` | POST | `CreateSessionView` | Pudhu chat session create pannum, `session_id` return pannum |
| `/api/chat/query/` | POST | `SubmitQueryView` | User question accept pannum, Celery task fire pannum, 202 return pannum |
| `/api/chat/<session_id>/` | GET | `SessionMessagesView` | Session-oda ellaa messages return pannum (polling-ku use pannum) |
| `/api/chat/catalog/` | GET | `LegalCatalogView` | Legal knowledge base search pannum (optional `?search=` parameter) |

### Serializers:

| Serializer | Fields | Purpose |
|---|---|---|
| `ChatSessionSerializer` | id, created_at | Session data serialize pannum |
| `LegalQuerySerializer` | id, status, user_query, ai_response, created_at, updated_at | Message data serialize pannum |
| `CreateLegalQuerySerializer` | session_id, user_query | Input validate pannum — session_id valid ah check pannum |

### SubmitQueryView — Detailed Flow:

```python
def post(self, request):
    # 1. Validate input using CreateLegalQuerySerializer
    # 2. Get session from session_id
    # 3. Create LegalQuery(session=session, user_query=query, status='pending')
    # 4. Fire Celery task: process_legal_query.delay(legal_query.id)
    # 5. Return Response({'query_id': ..., 'status': 'pending'}, status=202)
```

---

## 📌 8. Frontend Module

**File:** `frontend/src/App.jsx` (React + Tailwind CSS)

### What It Does:

1. **Page load aana udan** → `POST /api/chat/sessions/` call panni session create pannum.
2. **56 quick-question buttons** display aagum — user click panna directly query submit aagum.
3. **Text input box** irukku — custom question type pannalam.
4. **Submit aana udan** → `POST /api/chat/query/` call pannum → "Analyzing with RAG..." loading message kaatum.
5. **Every 2 seconds poll** pannum → `GET /api/chat/{sessionId}/` → pending messages irukka nu check pannum.
6. **Status "completed" aana** → answer display pannum in structured format.
7. **Error handling** — backend down, network issue → user-ku error message kaatum.

### State Variables:

```javascript
sessionId   → current chat session ID
query       → text input value
messages    → array of all messages (user questions + AI answers)
submitting  → true when query being sent
error       → error message string
hasPending  → true if any message status is "pending"
```

### UI Design:
- **Max width card** — centered, clean design
- **Title:** "Indian Legal Chatbot"
- **Quick buttons:** 56 pill-shaped buttons, click panna auto-submit
- **Message area:** 420px scrollable, user messages + AI responses
- **Input:** Text field + Send button
- **Loading:** "Analyzing with RAG..." pending message
- **Tailwind CSS** — full responsive styling

---

## 📌 9. Docker Compose — 5 Services

**File:** `docker-compose.yml`

Oru `docker-compose up --build` command-la project full-a start aagum.

### Services:

| Service | Image | Port | Enna Pannum |
|---|---|---|---|
| **redis** | `redis:7-alpine` | 6379 | Celery message broker — tasks queue maintain pannum |
| **ollama** | `ollama/ollama:latest` | 11434 | LLM server — llama3.2:3b model + nomic-embed-text model run pannum |
| **backend** | Custom (Python 3.11) | 8000 | Django server — first `rag_setup.py` run pannum (knowledge base build), then `migrate`, then `runserver` |
| **celery** | Same as backend | — | Celery worker — background-la AI tasks process pannum |
| **frontend** | Custom (Node 20) | 3000 | Vite dev server — React app serve pannum |

### Startup Order:
```
1. redis start aagum (no dependency)
2. ollama start aagum (no dependency)
3. backend start aagum (depends on redis + ollama)
   → rag_setup.py run aagi ChromaDB build aagum
   → migrate run aagi database tables create aagum
   → runserver start aagum
4. celery start aagum (depends on backend + redis + ollama)
5. frontend start aagum (depends on backend)
```

### Environment Variables:
```
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_EMBED_MODEL=nomic-embed-text
```

---

## 📌 10. Django Settings

**File:** `core/settings.py`

| Setting | Value | Purpose |
|---|---|---|
| Database | SQLite3 | Chat data store |
| Timezone | Asia/Kolkata | Indian Standard Time |
| CELERY_BROKER_URL | redis://localhost:6379/0 | Redis broker for tasks |
| CELERY_RESULT_BACKEND | redis://localhost:6379/1 | Redis for task results |
| OLLAMA_HOST | http://localhost:11434 | Ollama API endpoint |
| OLLAMA_MODEL | llama3.2:3b | LLM model name |
| OLLAMA_EMBED_MODEL | nomic-embed-text | Embedding model name |
| RAG_DATA_PATH | data/legal_sections.csv | Legal knowledge base file |
| CHROMA_PERSIST_DIR | chroma_db/ | ChromaDB persistent storage |
| INSTALLED_APPS | rest_framework, chat | DRF + chat app |

---

## 📌 11. Data Flow — Full Picture (Start to End)

```
┌──────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                       │
│                                                                │
│  1. Page load → POST /sessions/ → session_id kidaikum          │
│  2. User types "someone stole my bike" → Send click            │
│  3. POST /query/ {session_id, user_query}                      │
│  4. "Analyzing with RAG..." loading kaatum                     │
│  5. Every 2 sec → GET /{session_id}/ → status check            │
│  6. status="completed" → answer display                        │
└──────────┬───────────────────────────────────────────┬────────┘
           │ POST /query/                              │ GET /{id}/
           ▼                                           │
┌──────────────────────────────────────────────────────────────┐
│                    BACKEND (Django REST)                       │
│                                                                │
│  SubmitQueryView:                                              │
│  1. Validate input (serializer)                                │
│  2. Create LegalQuery(status='pending')                        │
│  3. process_legal_query.delay(id) → Celery fire                │
│  4. Return 202 Accepted                                        │
│                                                                │
│  SessionMessagesView:                                          │
│  1. Get all queries for session_id                             │
│  2. Return messages list with status                           │
└──────────┬───────────────────────────────────────────────────┘
           │ Celery task dispatch
           ▼
┌──────────────────────────────────────────────────────────────┐
│                    CELERY WORKER (Background)                  │
│                                                                │
│  process_legal_query(legal_query_id):                          │
│                                                                │
│  Step 1: Simple QA → "hi" / "FIR" / helpline → instant answer │
│       │                                                        │
│       ▼ (no match)                                             │
│  Step 2: Query Understanding                                   │
│       │  typo fix → phrase expand → intent detect → enrich     │
│       ▼                                                        │
│  Step 3: Best Entry Lookup                                     │
│       │  curated rules → scored search → confidence check      │
│       │  ≥ 0.42 → direct answer                               │
│       ▼ (< 0.42)                                               │
│  Step 4: RAG Retrieval                                         │
│       │  ChromaDB similarity_search(k=3)                       │
│       │  fallback: keyword search                              │
│       ▼                                                        │
│  Step 5: Ollama LLM                                            │
│       │  build_prompt → ask_ollama → structured response       │
│       │  fail → entry fallback → context fallback → default    │
│       ▼                                                        │
│  Step 6: Save → status='completed', ai_response=answer         │
└──────────────────────────────────────────────────────────────┘
           │                              │
           ▼                              ▼
┌─────────────────┐           ┌─────────────────┐
│    ChromaDB     │           │     Ollama      │
│  Vector Store   │           │   LLM Server    │
│                 │           │                 │
│ legal_sections  │           │ llama3.2:3b     │
│ embeddings      │           │ nomic-embed-text│
│ similarity      │           │ /api/generate   │
│ search          │           │ /api/tags       │
└─────────────────┘           └─────────────────┘
           │
           ▼
┌─────────────────┐
│     Redis       │
│  Message Broker │
│                 │
│ Task queue      │
│ Result store    │
└─────────────────┘
```

---

## 📌 12. Scoring System — Epdi Best Match Find Pannum

`_entry_score()` function — every candidate law entry-ku score calculate pannum:

```
Final Score = (Token Overlap × 0.70) + (Fuzzy Similarity × 0.30) + Bonuses

Token Overlap = matching_tokens / total_tokens
Fuzzy Similarity = SequenceMatcher.ratio(query, entry_text)

Bonuses:
  + exact section name match → +0.15
  + domain-specific booster (harassment, cyber, etc.) → +0.05 to +0.10
  - domain-specific penalty (unrelated topics) → -0.05

Confidence Thresholds:
  ≥ 0.42 → Direct answer (skip LLM)
  ≥ 0.32 → Include in candidates
  < 0.32 → Reject
```

---

## 📌 13. Fallback System — System Crash Aagaadhu

Project-la multiple safety layers irukku:

| Situation | Fallback |
|---|---|
| Simple greeting/FAQ | Simple QA instant answer |
| High confidence entry (≥0.42) | Direct formatted answer, no LLM needed |
| LLM service down | `format_response_from_entry()` or `format_response_from_context()` |
| LLM returns empty/bad format | Same fallback formatting |
| No matching entry at all | `get_default_guidance_response()` — generic guidance |
| ChromaDB embeddings fail | `_keyword_fallback()` — pure token matching |
| CSV data missing | `SEED_ROWS` — 7 built-in legal entries as fallback dataset |

**Key principle:** User eppavum oru response paarum — system eppavum crash pannama oru answer kudukum.

---

## 📌 14. Response Format — Always Same Structure

Every response — LLM generate pannaalum, direct entry-lirundhaalum, fallback aanaalum — same format:

```
LAW: [Act name - IPC, IT Act, etc.]
SECTION: [Section number and title]
PUNISHMENT: [Jail time, fine details]
NEXT STEPS: 1. [Step 1]  2. [Step 2]  3. [Step 3]
DISCLAIMER: Consult lawyer
```

**Yenda same format?** — User-ku consistent experience. Epdi read panranu theriyum. Confusion illa.

---

## 📌 15. Security & Safety Features

1. **Disclaimer ellaa response-layum** — "Consult a qualified lawyer" always irukum.
2. **Local AI** — Ollama locally run aagum, user data cloud-ku pogaadhu.
3. **No authentication needed** — Simple anonymous chat, no personal data collect pannala.
4. **Fallback chain** — Wrong answer kodukuradhavida, general guidance kudukum.
5. **Low confidence = safe response** — Confidence kuraivu na generic disclaimer kudukum.

---

## 📌 16. File-by-File Summary

| File | Lines | Purpose |
|---|---|---|
| `chat/rag_setup.py` | 1156 | RAG engine — vector store, scoring, synonym expansion, curated rules |
| `chat/query_understanding.py` | 368 | Query preprocessing — typo fix, intent detection, entity extraction |
| `chat/tasks.py` | 136 | Celery task — full APRM pipeline orchestration |
| `chat/simple_qa.py` | 119 | Quick FAQ answers + default fallback |
| `chat/views.py` | 63 | Django API views — session, query, messages, catalog |
| `chat/models.py` | 18 | Database models — ChatSession, LegalQuery |
| `chat/serializers.py` | 24 | DRF serializers — input validation |
| `chat/urls.py` | 10 | API URL routing |
| `core/settings.py` | 79 | Django + Celery + Ollama configuration |
| `core/celery.py` | 9 | Celery app setup |
| `core/urls.py` | 6 | Root URL config |
| `frontend/src/App.jsx` | 173 | React chat UI — full single-page app |
| `docker-compose.yml` | 62 | Docker orchestration — 5 services |

---

## 📌 17. Numbers at a Glance

| What | Count |
|---|---|
| Total intent categories | 37 |
| Typo corrections | 80+ |
| Phrase aliases | 75+ |
| Phrase normalization rules | 130+ |
| Synonym groups | 45+ |
| Keyword enrichment rules | 50+ |
| Curated legal mappings | 80+ |
| Quick-question suggestions | 56 |
| Seed legal entries (fallback) | 7 |
| API endpoints | 4 |
| Database models | 2 |
| Docker services | 5 |
| Fallback levels | 3 |

---

> **Summary:** Indha project oru full-stack AI legal chatbot. User simple English-la question kekalam → APRM pipeline (Analyze → Process → Retrieve → Model) run aagum → structured legal answer varum with LAW, SECTION, PUNISHMENT, NEXT STEPS, DISCLAIMER. Multiple fallback layers irukku so system eppavum crash aagaadhu. Docker Compose use panni oru command-la full system start pannalam. Ellam local-a run aagum — privacy safe, fast, reliable.
