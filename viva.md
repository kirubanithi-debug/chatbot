# Law Chatbot Project - Viva Notes (Thanglish)

## 1) Project la naanga enna pannom? (What we done)
Indha project la naanga **Indian legal issues ku AI based chatbot** create pannirukkom. User simple ah problem type panna (example: "bike stolen", "salary not paid", "no road in my street") system:

- related law/section identify pannum
- punishment details kudukkum
- next legal steps suggest pannum
- final la safety disclaimer kudukkum ("Consult lawyer")

### Core implementation done:
- Django REST backend setup pannom
- React frontend chat UI build pannom
- Chat session & message storage model create pannom
- Celery + Redis use panni async query processing pannom
- RAG pipeline create pannom using legal_sections.csv + Chroma vector DB
- Ollama LLM integration pannom for response generation
- Query understanding layer create pannom (intent detection, typo correction, phrase normalization)
- Simple FAQ responses add pannom (FIR, helpline, cyber complaint)
- Docker compose la full stack run aagura setup pannom

---

## 2) Abstract
Indha project oda main aim, normal users ku legal help easy ah kidaikkanum nu. Romba perukku legal terms puriyadhu, correct section kandupidikka kashtam. Adhanala naanga one AI legal assistant chatbot build pannom. User oda query receive pannitu, legal knowledge base la search pannitu, best possible law info format la kudukkum.

Output structured format la irukkum:
- LAW
- SECTION
- PUNISHMENT
- NEXT STEPS
- DISCLAIMER

Idhu legal awareness improve pannum, first-level guidance fast ah kudukkum.

---

## 3) Existing System
Existing system la generally:

- User manual ah lawyer kita poi basic info kekkanum
- Internet la random websites la search pannanum
- Correct law section identify panna confusion irukkum
- Time waste aagum
- Common people ku legal language difficult ah irukkum

### Existing system problems:
- 24x7 immediate response illa
- Personalized issue mapping weak
- Typo/colloquial query handling illa
- Structured legal guidance illa

---

## 4) Proposed System
Proposed system la naanga **AI + RAG based legal chatbot** implement pannom.

### Flow:
1. User frontend la query anuppuvanga
2. Backend session create pannum, query save pannum
3. Celery worker async ah query process pannum
4. Query understanding module typo fix + intent detect pannum
5. RAG layer legal knowledge base la best match kandupidikkum
6. Ollama model final structured response generate pannum
7. UI la user ku result display aagum

### Special features:
- Quick question chips (ready-made prompts)
- Polling based live response update
- Simple Q&A direct fallback
- Context illa na safe guidance response

---

## 5) Advantages (Advandace)
Indha system oda mukkiya advantages:

- **Fast response**: manual search vida vegama legal direction kidaikkum
- **User-friendly**: simple language la query kudutha podhum
- **Typo tolerant**: wrong spelling irundhalum understand pannum
- **Structured output**: law/section/punishment/steps clear ah varum
- **Scalable architecture**: Celery async processing nala multi requests handle pannum
- **Offline capable AI stack**: Ollama local model use panna mudiyum
- **Domain focused**: legal issue specific knowledge base use pannudhu

---

## 6) Tech Stack

### Frontend:
- React
- Vite
- Axios
- Tailwind CSS

### Backend:
- Django 5.1
- Django REST Framework
- Celery
- Redis

### AI / RAG:
- Ollama (llama3.2:3b)
- Ollama Embeddings (nomic-embed-text)
- LangChain
- ChromaDB
- Pandas

### Database:
- SQLite (chat session + query history)
- Chroma persistent DB (vector search)

### Deployment / Runtime:
- Docker
- Docker Compose

---

## 7) Module Explain (Viva ku useful)

### a) Frontend Module
React app la chat interface irukku. Session start pannitu, user query send pannum. Response pending/completed status UI la kaamikum. Quick suggestions buttons irukku.

### b) API Module
Django REST endpoints:
- create session
- submit query
- fetch session messages
- legal catalog fetch

### c) Async Processing Module
Heavy AI processing direct request cycle la panna delay varum. Adhanala Celery worker use pannom. Redis broker la tasks queue panni background la process pannrom.

### d) Query Understanding Module
User text la spelling mistakes, colloquial words, phrase aliases normalize pannum. Intent detect panni proper legal retrieval ku query enrich pannum.

### e) RAG Knowledge Module
`legal_sections.csv` la irukkura law data embed panni Chroma la store pannrom. Query vandha top relevant legal entries retrieve pannrom.

### f) LLM Response Module
Retrieved context base panni Ollama model answer generate pannum. Format strict ah enforce pannom so response consistent ah irukkum.

### g) Fallback / Safety Module
Context weak irundha default legal guidance kudukkum. Every response la disclaimer include pannrom: "Consult lawyer".

---

## 8) Conclusion
Indha project legal domain la **practical first-level AI assistant** maari work pannudhu. Manual legal searching kashtatha reduce pannudhu. User ku instant direction kudukkudhu. Future la multilingual support, more law datasets, voice input, advanced case-specific workflows add panna mudiyum.

---

## 9) Viva la solla short pitch (30 seconds)
"Namma project oru AI based Indian legal chatbot. User simple ah issue type pannina, system legal knowledge base + LLM use panni law section, punishment, next steps structured ah kudukkum. Django backend, React frontend, Celery async queue, Redis, Chroma RAG, Ollama model use pannirukkom. Idhu legal awareness improve pannum and first-level guidance fast ah kudukkum."

---

## 10) All Laws (Project Annexure)

- Project la use panna **total unique law entries: 183**
- Full list inga irukku: `ALL_LAWS.md`
- Source dataset: `backend/data/legal_sections.csv`

### Viva point (short answer)
"All curated law mappings backend la verify pannirukkom. `rag_setup.py` la irukkura pick rules ellam dataset la match aagudhu. Missing mappings: 0."

---

## 11) Journal + Prompt Document

- Project journal and prompt bank ready panniten: `PROJECT_JOURNAL_AND_PROMPTS.md`
- Idha daily progress, demo run, and viva explanation ku use pannalaam.