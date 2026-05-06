# RuralShiksha API Documentation

## Base URL

```
http://localhost:8000/api/
https://your-domain.com/api/  (production)
```

## Authentication

All endpoints except `/login` and `/register` require JWT authentication.

**Header format:**
```
Authorization: Bearer <access_token>
```

## Response Format

### Success Response (200/201)
```json
{
  "data": {...},
  "message": "Success",
  "status": 200
}
```

### Error Response (400/401/403/500)
```json
{
  "error": "Error message",
  "status": 400,
  "details": {...}
}
```

## Authentication Endpoints

### POST `/auth/register/`

Register new student or teacher.

**Request:**
```json
{
  "user": {
    "username": "student1",
    "email": "student@test.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePass123!"
  },
  "grade": 7,
  "school_name": "Central School"
}
```

**Response (201):**
```json
{
  "user_id": "uuid",
  "username": "student1",
  "email": "student@test.com",
  "role": "student"
}
```

---

### POST `/auth/login/`

Authenticate and get JWT tokens.

**Request:**
```json
{
  "username": "student1",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access": "eyJhbGc...",
  "refresh": "eyJhbGc...",
  "user": {
    "id": "uuid",
    "username": "student1",
    "role": "student"
  }
}
```

---

### POST `/auth/refresh/`

Get new access token using refresh token.

**Request:**
```json
{
  "refresh": "eyJhbGc..."
}
```

**Response (200):**
```json
{
  "access": "eyJhbGc..."
}
```

---

## User Endpoints

### GET `/users/profile/`

Get current user's profile.

**Response (200):**
```json
{
  "id": "uuid",
  "username": "student1",
  "email": "student@test.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+919876543210",
  "school_name": "Central School",
  "role": "student",
  "created_at": "2026-01-15T10:30:00Z"
}
```

---

### PUT `/users/profile/`

Update user profile.

**Request:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+919876543210"
}
```

**Response (200):** Updated profile object

---

### GET `/users/dashboard/`

Get student dashboard data.

**Response (200):**
```json
{
  "student": {
    "id": "uuid",
    "grade": 7,
    "school_name": "Central School"
  },
  "subjects": {
    "Maths": {
      "avg_score": 78,
      "chapters_completed": 4,
      "next_chapter": "Chapter 5"
    },
    "English": { ... },
    "Science": { ... },
    "Social Science": { ... },
    "Kannada": { ... }
  },
  "total_quiz_attempts": 12,
  "ai_tutor_sessions": 5,
  "attendance": 85
}
```

---

## Quiz Endpoints

### GET `/quizzes/`

List quizzes with filters.

**Query Parameters:**
- `grade` (optional): Student grade (1-10)
- `subject` (optional): Subject name
- `chapter` (optional): Chapter number
- `page` (optional): Pagination (default: 1)

**Example:**
```
GET /api/quizzes/?grade=7&subject=Maths
```

**Response (200):**
```json
{
  "count": 15,
  "next": "/api/quizzes/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "title": "Algebra Basics",
      "subject": "Maths",
      "grade": 7,
      "num_questions": 10,
      "duration_minutes": 30,
      "is_published": true
    }
  ]
}
```

---

### GET `/quizzes/{id}/`

Get quiz details with questions.

**Response (200):**
```json
{
  "id": "uuid",
  "title": "Algebra Basics",
  "subject": "Maths",
  "grade": 7,
  "num_questions": 10,
  "duration_minutes": 30,
  "questions": [
    {
      "id": "q1",
      "question_text": "What is 2x + 3 = 11?",
      "question_type": "mcq",
      "options": ["x=2", "x=3", "x=4", "x=5"],
      "marks": 1
    }
  ]
}
```

---

### POST `/quizzes/{id}/submit/`

Submit quiz answers and get grading.

**Request:**
```json
{
  "answers": {
    "q1": "x=4",
    "q2": "true",
    "q3": "b"
  }
}
```

**Response (200):**
```json
{
  "score": 8,
  "total_marks": 10,
  "percentage": 80,
  "passed": true,
  "feedback": {
    "q1": { "correct": true, "explanation": "..." },
    "q2": { "correct": false, "correct_answer": "false" }
  }
}
```

---

### GET `/students/quizzes/history/`

Get student's quiz history.

**Query Parameters:**
- `subject` (optional): Filter by subject
- `page` (optional): Pagination

**Response (200):**
```json
{
  "count": 5,
  "results": [
    {
      "id": "attempt-uuid",
      "quiz": "uuid",
      "quiz_title": "Algebra Basics",
      "score": 8,
      "total_marks": 10,
      "percentage": 80,
      "passed": true,
      "submitted_at": "2026-01-20T14:30:00Z"
    }
  ]
}
```

---

## AI Tutor Endpoints

### POST `/ai-tutor/sessions/`

Create new tutor session.

**Request:**
```json
{
  "subject": "Maths",
  "language": "en"  // "en" or "kn"
}
```

**Response (201):**
```json
{
  "id": "session-uuid",
  "subject": "Maths",
  "language": "en",
  "message_count": 0,
  "is_active": true,
  "created_at": "2026-01-20T14:30:00Z"
}
```

---

### GET `/ai-tutor/sessions/`

List all tutor sessions.

**Response (200):**
```json
{
  "count": 3,
  "results": [
    {
      "id": "session-uuid",
      "subject": "Maths",
      "language": "en",
      "message_count": 5,
      "is_active": true,
      "messages": [
        {
          "role": "student",
          "content": "How do I solve quadratic equations?",
          "created_at": "2026-01-20T14:30:00Z"
        },
        {
          "role": "tutor",
          "content": "Quadratic equations...",
          "created_at": "2026-01-20T14:31:00Z"
        }
      ]
    }
  ]
}
```

---

### POST `/ai-tutor/sessions/{id}/send_message/`

Send message to AI tutor (streaming response).

**Request:**
```json
{
  "message": "How do I solve 2x + 3 = 7?"
}
```

**Response (200 - Server-Sent Events):**
```
data: {"role":"tutor","chunk":"To solve the"}
data: {"role":"tutor","chunk":" equation 2x"}
data: {"role":"tutor","chunk":" + 3 = 7:"}
...
```

---

### POST `/ai-tutor/sessions/{id}/close/`

Close tutor session.

**Response (200):**
```json
{
  "id": "session-uuid",
  "is_active": false,
  "message_count": 5
}
```

---

## Resource Endpoints

### GET `/resources/`

List resources by grade/subject.

**Query Parameters:**
- `grade` (optional): Grade level
- `subject` (optional): Subject name
- `chapter` (optional): Chapter number

**Example:**
```
GET /api/resources/?grade=7&subject=Maths&chapter=5
```

**Response (200):**
```json
{
  "count": 8,
  "results": [
    {
      "id": "uuid",
      "title": "Chapter 5 Notes",
      "description": "Detailed notes on algebra",
      "resource_type": "pdf",
      "grade": 7,
      "subject": "Maths",
      "chapter": 5,
      "file_size": 2048000,
      "download_count": 42,
      "uploaded_by": "teacher1",
      "uploaded_at": "2026-01-10T10:00:00Z"
    }
  ]
}
```

---

### GET `/resources/{id}/download/`

Download resource (marks as downloaded for analytics).

**Response (200):**
```json
{
  "download_url": "signed-s3-url-or-file-path",
  "file_name": "chapter5_notes.pdf",
  "file_size": 2048000
}
```

---

### POST `/resources/upload/`

Upload new resource (teacher only).

**Request (multipart/form-data):**
- `title`: string
- `description`: string
- `grade`: integer (1-10)
- `subject`: string
- `chapter`: integer
- `resource_type`: "pdf" | "video" | "lesson" | "notes"
- `file`: binary

**Response (201):**
```json
{
  "id": "uuid",
  "title": "Chapter 5 Notes",
  "resource_type": "pdf",
  "grade": 7,
  "subject": "Maths",
  "file_url": "/media/resources/chapter5.pdf"
}
```

---

## Doubt Session Endpoints

### POST `/doubts/create/`

Create new doubt session.

**Request:**
```json
{
  "subject": "Maths",
  "title": "Quadratic equations",
  "description": "How to solve quadratic equations?"
}
```

**Response (201):**
```json
{
  "id": "session-uuid",
  "subject": "Maths",
  "title": "Quadratic equations",
  "status": "waiting_for_teacher",
  "created_at": "2026-01-20T14:30:00Z"
}
```

---

### GET `/doubts/{session_id}/`

Get doubt session details with messages.

**Response (200):**
```json
{
  "id": "session-uuid",
  "subject": "Maths",
  "title": "Quadratic equations",
  "status": "active",
  "student": { "id": "uuid", "name": "John" },
  "teacher": { "id": "uuid", "name": "Ms. Smith" },
  "messages": [
    {
      "id": "msg-uuid",
      "sender": "John",
      "content": "How to solve?",
      "timestamp": "2026-01-20T14:30:00Z"
    },
    {
      "id": "msg-uuid",
      "sender": "Ms. Smith",
      "content": "Use the quadratic formula...",
      "timestamp": "2026-01-20T14:35:00Z"
    }
  ]
}
```

---

### GET `/students/doubts/`

List all student's doubt sessions.

**Query Parameters:**
- `status` (optional): "open" | "resolved"
- `page` (optional): Pagination

**Response (200):**
```json
{
  "count": 5,
  "results": [
    {
      "id": "session-uuid",
      "subject": "Maths",
      "title": "Quadratic equations",
      "status": "resolved",
      "created_at": "2026-01-20T14:30:00Z"
    }
  ]
}
```

---

## Notification Endpoints

### GET `/notifications/`

Get user notifications.

**Query Parameters:**
- `type` (optional): "quiz_result" | "marks_update" | "doubt_resolved"
- `read` (optional): true | false
- `page` (optional): Pagination

**Response (200):**
```json
{
  "count": 10,
  "results": [
    {
      "id": "uuid",
      "type": "quiz_result",
      "title": "Quiz Result",
      "message": "You scored 85% in Algebra Quiz",
      "read": false,
      "created_at": "2026-01-20T14:30:00Z"
    }
  ]
}
```

---

### PUT `/notifications/{id}/read/`

Mark notification as read.

**Response (200):**
```json
{
  "id": "uuid",
  "read": true
}
```

---

## Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | User lacks permission |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Unique constraint violation |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Backend error |

---

## Rate Limiting

API requests are limited to:
- **Anonymous users**: 100 requests/hour
- **Authenticated users**: 1000 requests/hour
- **Per endpoint**: 50 requests/minute

**Headers returned:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1642689600
```

---

## Pagination

All list endpoints support pagination:

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response:**
```json
{
  "count": 150,
  "next": "/api/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Filtering & Searching

Supported on most list endpoints:

**Query Parameters:**
- `search`: Search by title/content
- `grade`: Filter by grade
- `subject`: Filter by subject
- `status`: Filter by status
- `ordering`: Sort by field (-created_at for descending)

**Example:**
```
GET /api/quizzes/?grade=7&subject=Maths&ordering=-created_at
```

---

## API Testing with cURL

```bash
# Register
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "user": {"username": "test", "email": "test@test.com", "password": "pass"},
    "grade": 5
  }'

# Login
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "pass"}'

# Get dashboard (with token)
curl -X GET http://localhost:8000/api/users/dashboard/ \
  -H "Authorization: Bearer <token>"

# List quizzes
curl -X GET "http://localhost:8000/api/quizzes/?grade=7&subject=Maths"

# Submit quiz
curl -X POST http://localhost:8000/api/quizzes/<quiz-id>/submit/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"answers": {"q1": "a", "q2": "b"}}'
```

---

## Webhook Events (Future Implementation)

Future versions will support webhooks for:
- Quiz submission completion
- AI tutor session start/end
- Doubt resolution
- SMS delivery status

Subscribe via settings endpoint.
