# Phase 4: AI Tutor Integration - Testing Guide

## Overview
Phase 4 integrates streaming AI chat powered by Ollama with the React frontend. Students can create tutor sessions, ask questions, and receive curriculum-aware responses in English or Kannada.

## Prerequisites

### 1. Start Ollama Server
```bash
# On your local machine or server where Ollama is installed
ollama serve

# In another terminal, pull the model if needed
ollama pull llama3
```

### 2. Backend Setup
```bash
cd backend
python manage.py runserver
```

### 3. Frontend Setup
```bash
cd frontend
npm run dev
```

## Architecture

### Backend Flow
```
POST /api/ai-tutor/sessions/
  ├─ Create TutorSession with grade, subject, language
  └─ Initialize ConversationMetrics

POST /api/ai-tutor/sessions/{id}/send_message/
  ├─ Extract student message
  ├─ Load conversation history from DB
  ├─ Query Ollama API with curriculum-aware prompt
  ├─ Stream response via Server-Sent Events (SSE)
  └─ Save tutor response to SessionMessage
```

### Frontend Flow
```
AITutor Component
  ├─ Manage sessions list (sidebar)
  ├─ Create new session with subject + language selector
  ├─ Fetch messages from backend
  ├─ Send message via fetch() streaming API
  ├─ Parse SSE chunks
  ├─ Update messages in real-time
  └─ Display ChatMessage components
```

## Testing Steps

### Step 1: Create a New Session
1. Click **"+ New Session"** in the sidebar
2. Select subject (e.g., "Mathematics")
3. Select language (e.g., "English")
4. Click **"Create"**
5. Verify session appears in sidebar

### Step 2: Send a Question
1. In the chat input at bottom, type a question:
   - "What is a quadratic equation?"
   - "How do I solve 2x + 5 = 15?"
   - "Explain photosynthesis"
2. Click **"Send"** or press Enter
3. Verify:
   - Message appears in blue bubble on right
   - "Tutor thinking..." indicator shows
   - Streamed response appears in white bubble (left side)

### Step 3: Test Streaming
- Watch the response build character-by-character
- Verify no truncation or missing text
- Check that long responses scroll properly

### Step 4: Test Multiple Sessions
1. Create a second session with different subject
2. Switch between sessions using sidebar buttons
3. Verify message history loads correctly for each

### Step 5: Test Language Support
1. Create session in "Kannada"
2. Send question in Kannada (or any language)
3. Verify tutor responds in Kannada with ಅ, ಕ, ನ characters

## Expected Responses

### Mathematics Question
**Input:** "How to solve 2x + 3 = 7?"
**Expected:** Step-by-step explanation of isolating x

### Science Question
**Input:** "What is photosynthesis?"
**Expected:** Curriculum-aligned explanation for student's grade

### Kannada Mode
**Input:** ಕ್ವೇಶ್ಚನ್ (Any Kannada question)
**Expected:** ರೆಸ್ಪನ್ಸ್ in Kannada

## API Endpoints

### Create Session
```bash
POST http://localhost:8000/api/ai-tutor/sessions/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "subject": "maths",
  "language": "en"
}
```

### Send Message (Streaming)
```bash
POST http://localhost:8000/api/ai-tutor/sessions/{session_id}/send_message/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "message": "What is a quadratic equation?"
}

# Response: Server-Sent Events (text/event-stream)
data: {"chunk": "A quadratic equation"}
data: {"chunk": " is an equation"}
data: {"chunk": " of the form ax²..."}
```

## Debugging

### Issue: "Cannot connect to Ollama"
- Check Ollama server is running: `curl http://localhost:11434/api/tags`
- Verify `OLLAMA_API_URL` in backend `.env`
- Ensure backend can reach Ollama (firewall, network)

### Issue: Streaming stops prematurely
- Check browser console for errors
- Verify backend API endpoint returns proper SSE format
- Check network tab in DevTools for partial responses

### Issue: No messages appear
- Verify JWT token is valid
- Check API response in browser Network tab
- Ensure session was created successfully
- Check backend logs for errors

### Issue: Ollama response is generic/not curriculum-aware
- Verify curriculum prompt is being injected in `ollama_client.py`
- Check student grade is correct in DB
- Ensure subject matches a mapped subject in curriculum map

## Components

### src/components/Student/AITutor.jsx
- Main component with session management
- Handles message sending and streaming
- Manages subject/language selection
- Updates messages in real-time

### src/components/Student/ChatMessage.jsx
- Renders individual message bubbles
- Different styling for student vs tutor
- Shows timestamp

### src/utils/api.js
- Axios instance with JWT interceptors
- Handles authentication headers
- Automatic token refresh on 401

## Next Steps (Phase 5)
- Implement real-time doubt chat with WebSocket
- Add teacher-student interaction
- Implement file sharing in messages

## Notes
- Streaming is CPU-intensive; Ollama may take 5-30 seconds per response
- First response takes longer (model warm-up)
- Large responses may take minutes to stream
- Test with small, targeted questions first
- Monitor Ollama server logs for errors

## File Reference
- Backend: `backend/ai_tutor/views.py`, `backend/ai_tutor/ollama_client.py`
- Frontend: `frontend/src/components/Student/AITutor.jsx`
- API: `POST /api/ai-tutor/sessions/{id}/send_message/`
