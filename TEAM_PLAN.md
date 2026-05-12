# RuralSiksha — 6-Person Team Plan (Demo May 2026)

## Project Architecture

```
backend/                       Django + DRF, port 8000
├── common/ollama.py          Shared LLM client (USE THIS in every module)
├── users/                    Auth, registration, JWT
├── study_hub/                ✅ Module 1 - DONE
├── ai_tutor/                 ✅ Module 2 - DONE (chapter-scoped)
├── quizzes/                  Module 3 - skeleton ready
├── schemes/                  Module 4 - to create
├── careers/                  Module 5 - to create
└── resources/                Module 6 - skeleton ready (offline)

frontend/                      React + Vite, port 5173
└── src/components/Student/
    ├── StudyHub.jsx          ✅ DONE
    ├── AITutor.jsx           ✅ DONE
    ├── QuizModule.jsx        skeleton (to upgrade for adaptive logic)
    ├── SchemesChat.jsx       to create
    ├── CareerGuidance.jsx    to create
    └── OfflineResourceBrowser.jsx  skeleton ready
```

## Tech Stack (already configured)

| Layer | Tech | Where |
|---|---|---|
| Backend | Django 4.2 + DRF | `backend/` |
| Frontend | React 18 + Vite | `frontend/` |
| DB | SQLite (dev) → switch to PostgreSQL for production | `settings.py` |
| AI | Ollama llama3 @ localhost:11434 | `common/ollama.py` |
| Auth | JWT (1h access, 7d refresh) | `users/` |
| Languages | en, hi, ta, te, bn, kn, mr | `LANGUAGE_NAMES` dict |
| Syllabi | CBSE, ICSE, KARNATAKA, MAHARASHTRA, TAMILNADU, WESTBENGAL, ANDHRAPRADESH | `study_hub/models.py` |

## Prerequisites Each Member Must Install

```powershell
# Python 3.10+
python --version

# Node 18+
node --version

# Ollama (download from ollama.com)
ollama serve              # keeps running
ollama pull llama3        # ~4 GB download, do once
```

---

## Module Ownership (one per teammate)

### 🟢 Module 1: Smart Study Hub — DONE (reference implementation)
**Files:** `backend/study_hub/*`, `frontend/src/components/Student/StudyHub.jsx`
**Endpoint:** `POST /api/study-hub/generate/`
**Status:** Working. Use this as the template for your own module.

### 🟢 Module 2: AI Tutor Chat — DONE (chapter-scoped)
**Files:** `backend/ai_tutor/*`, `frontend/src/components/Student/AITutor.jsx`
**Endpoints:**
- `POST /api/ai-tutor/sessions/` — create chapter-scoped session
- `POST /api/ai-tutor/sessions/{id}/send_message/` — stream replies
**System prompt:** `backend/ai_tutor/views.py` → `build_tutor_system_prompt()`
**Status:** Backend done. Frontend already exists; just pass `grade/syllabus/chapter` when creating a session.

---

### 🟡 Module 3: Adaptive Quiz Engine — Owner: ___________
**Goal:** 3 MCQs per chapter; difficulty (easy/medium/hard) auto-adjusts based on last 3 attempts.

**What to build:**
1. **Backend** (`backend/quizzes/`):
   - Update `Quiz` model — add `chapter` and `difficulty` fields (already partly exists)
   - New endpoint: `GET /api/quizzes/adaptive/?chapter=X&grade=Y` returns 3 questions whose difficulty depends on the student's recent average:
     - Recent avg < 40% → 3 EASY
     - 40-70% → 3 MEDIUM
     - > 70% → 3 HARD
   - Use the SAME `common.ollama.chat()` to GENERATE questions for chapters that don't have any:
     ```python
     prompt = f"Generate 3 {difficulty} MCQs for Grade {grade} {subject} chapter '{chapter}'. Reply as JSON: [{{question, options:[a,b,c,d], correct:'a'}}]"
     ```
2. **Frontend** (`frontend/src/components/Student/QuizModule.jsx`):
   - Already exists. Add a "🎯 Adaptive Practice" button that calls the new endpoint.
   - After submit, show difficulty trend ("You're now at Medium level!").

**Estimate:** 4-5 days

---

### 🟡 Module 4: Schemes & Scholarships RAG — Owner: ___________
**Goal:** Chatbot answers questions about Indian government schemes using REAL PDF documents.

**What to build:**
1. **Folder:** `backend/schemes/data/` — drop PDFs (e.g., PMJDY, NSP, KVPY, post-matric scholarships)
2. **Tools to install:**
   ```powershell
   pip install pypdf chromadb sentence-transformers
   ```
3. **Backend** (`backend/schemes/`):
   - `ingest.py` — script that reads PDFs, splits into chunks, stores embeddings in ChromaDB
   - `views.py` — endpoint `POST /api/schemes/ask/` that:
     1. Embeds the user's question
     2. Finds top 4 most-similar chunks from ChromaDB
     3. Sends question + chunks to Ollama as context
     4. Returns the answer + which PDFs/pages were cited
4. **Frontend** (`frontend/src/components/Student/SchemesChat.jsx`):
   - Simple chat UI similar to AITutor.jsx
   - Show source citations under each answer

**Pattern (copy-paste-ready):**
```python
# schemes/rag.py
from common.ollama import chat
def answer_scheme_question(question, chunks):
    context = "\n\n".join(chunks)
    prompt = f"Using ONLY this context, answer the question.\n\nContext:\n{context}\n\nQuestion: {question}"
    return chat([{"role": "user", "content": prompt}],
                system_prompt="You are a helpful assistant explaining Indian government schemes to students.")
```

**Estimate:** 6-7 days (RAG is the trickiest module)

---

### 🟡 Module 5: Career Guidance — Owner: ___________
**Goal:** For Grades 8-10 only. Looks at the student's quiz performance + interests, recommends 3 career paths.

**What to build:**
1. **Backend** (`backend/careers/`):
   - Model: `CareerInterest` — student selects up to 5 things they enjoy (Math, Art, Computers, Science, Helping Others, etc.)
   - Endpoint: `POST /api/careers/recommend/`
     - Pulls student's average score per subject from `quizzes`
     - Pulls their interests
     - Sends to Ollama: "Given this student's strengths and interests, suggest 3 careers in India"
     - Stores result so we don't regenerate every time
2. **Frontend** (`frontend/src/components/Student/CareerGuidance.jsx`):
   - Step 1: checkbox grid of interests
   - Step 2: results page with 3 career cards (title, what they do, subjects to focus on, sample salary, college path)

**Important:** Show this option ONLY if `user.grade >= 8`.

**Estimate:** 4 days

---

### 🟡 Module 6: Offline Mode — Owner: ___________
**Goal:** Pre-downloaded lessons available without internet.

**What to build:**
1. **Backend** (`backend/resources/`):
   - Already has `Resource` model
   - Add endpoint: `GET /api/resources/offline-pack/?grade=5&syllabus=CBSE` — returns ALL lessons + quizzes + cached Study Hub summaries for that grade as a single JSON file
2. **Frontend** (`frontend/src/utils/db.js`):
   - Already exists (IndexedDB wrapper). Use it.
   - Add a "📥 Download for offline" button on Study Hub
   - When clicked: fetch the offline pack, save every lesson into IndexedDB
   - When offline (`navigator.onLine === false`), the StudyHub component reads from IndexedDB instead of calling the API
3. **Service Worker** (`frontend/public/service-worker.js`):
   - Already configured. Just add the new API URLs to the cache list.

**Estimate:** 4 days

---

## Sprint Plan (5 sprints, 4 weeks each)

| Sprint | What everyone delivers |
|---|---|
| **Sprint 1** (Weeks 1-4)  | Setup local dev, Ollama running, demo Study Hub + AI Tutor work end-to-end. |
| **Sprint 2** (Weeks 5-8)  | Module 3 (Quiz) backend + Module 4 (RAG) ingest + Module 6 IndexedDB write. |
| **Sprint 3** (Weeks 9-12) | All modules wired in frontend. First end-to-end student flow: register → study → quiz → career. |
| **Sprint 4** (Weeks 13-16)| Polish: error handling, loading states, empty states, language switching across all modules. |
| **Sprint 5** (Weeks 17-20)| Testing, demo data seeding, deployment. **Demo Day = early May 2026.** |

## How to Test Your Module

```powershell
# Backend tests
cd backend
python manage.py test study_hub
python manage.py test ai_tutor

# Frontend tests (whoever sets it up)
cd frontend
npm test
```

## Common Code Patterns to Reuse

### 1. Calling Ollama (use everywhere)
```python
from common.ollama import chat
reply = chat(
    messages=[{"role": "user", "content": "Hello!"}],
    system_prompt="You are a helpful tutor.",
)
```

### 2. Streaming (chat that types out word-by-word)
See `ai_tutor/views.py → send_message()` for the full pattern.

### 3. Caching expensive AI generations
See `study_hub/views.py → generate_lesson()` — uses `get_or_create()` to avoid regenerating.

### 4. JWT-protected endpoint
```python
from rest_framework.permissions import IsAuthenticated
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def my_endpoint(request):
    user = request.user  # logged-in student
    ...
```

### 5. Calling an API from React
```javascript
import api from '../../utils/api';
const response = await api.post('/study-hub/generate/', { grade: 5, ... });
```

## Quick Reference: Run the Project

```powershell
# Terminal 1 - Ollama
ollama serve

# Terminal 2 - Backend
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Terminal 3 - Frontend
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 → Login as `demo` / `demo123` → click **Smart Study Hub**.

## Rules of the Road (so beginners don't get stuck)

1. ✅ **DO** copy the Study Hub pattern for new modules.
2. ✅ **DO** put prompts in their own `prompts.py` file.
3. ✅ **DO** cache AI responses in the database whenever possible.
4. ❌ **DON'T** make a new HTTP client for Ollama — use `common.ollama.chat()`.
5. ❌ **DON'T** put real student personal data in prompts you log.
6. ❌ **DON'T** push API keys to git — use the `.env` file.
7. 🆘 **WHEN STUCK:** open a Pull Request with `[help wanted]` in the title; another teammate reviews.
