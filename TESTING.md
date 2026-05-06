# RuralShiksha Testing Guide

## Running Tests

### Backend Tests

```bash
# Run all tests
docker-compose exec backend python manage.py test

# Run specific app tests
docker-compose exec backend python manage.py test users
docker-compose exec backend python manage.py test quizzes
docker-compose exec backend python manage.py test ai_tutor

# Run with coverage
docker-compose exec backend pip install coverage
docker-compose exec backend coverage run --source='.' manage.py test
docker-compose exec backend coverage report
docker-compose exec backend coverage html  # Generate HTML report
```

### Test Categories

#### 1. User Authentication Tests (`backend/users/tests.py`)
- ✅ Student registration with validation
- ✅ Teacher registration
- ✅ Login with JWT tokens
- ✅ Token refresh mechanism
- ✅ Protected endpoint access control
- ✅ User profile updates

**Run:**
```bash
docker-compose exec backend python manage.py test users
```

#### 2. Quiz Auto-Grading Tests (`backend/quizzes/tests.py`)
- ✅ Perfect score calculation
- ✅ Partial credit scoring
- ✅ Zero score handling
- ✅ Unique quiz attempt enforcement
- ✅ Filtering by grade/subject
- ✅ Quiz submission API

**Run:**
```bash
docker-compose exec backend python manage.py test quizzes
```

#### 3. AI Tutor Tests (`backend/ai_tutor/tests.py`)
- ✅ Session creation (English & Kannada)
- ✅ Message logging
- ✅ Session closure
- ✅ Curriculum-aware prompts
- ✅ Ollama API integration (mocked)

**Run:**
```bash
docker-compose exec backend python manage.py test ai_tutor
```

### Frontend Tests

```bash
# Install test dependencies
cd frontend && npm install

# Run Jest tests
npm test

# Run E2E tests (Cypress)
npm run cypress:open  # Interactive mode
npm run cypress:run   # Headless mode

# Watch mode
npm test -- --watch
```

## Manual Testing Checklist

### Authentication Flow
- [ ] Register as student → success with JWT
- [ ] Login → receive access + refresh tokens
- [ ] Access protected endpoint without token → 401
- [ ] Access with valid token → success
- [ ] Refresh token → new access token
- [ ] Logout clears localStorage

### Student Dashboard
- [ ] Load dashboard → shows grade, quiz count, tutor sessions
- [ ] Subject cards display → avg score and progress bar
- [ ] Quick action buttons → navigate to correct pages
- [ ] Offline mode indicator when offline

### Quiz Module
- [ ] Browse quizzes → filtered by grade/subject
- [ ] Load quiz → all questions visible
- [ ] Submit quiz → instant feedback with score
- [ ] View quiz history → all past attempts shown
- [ ] Can't retake quiz → unique constraint enforced
- [ ] Offline attempt → saved to pending_actions

### AI Tutor
- [ ] Create session → works in English and Kannada
- [ ] Send message → streams response from Ollama
- [ ] Multiple sessions → can switch between them
- [ ] Session history → messages persist
- [ ] Offline message → queued for sync

### Resources
- [ ] Browse resources → listed by subject
- [ ] Download resource → saved to IndexedDB
- [ ] Offline access → load from IndexedDB
- [ ] File opening → launches PDF/video

### Offline Features
- [ ] OfflineIndicator shows → when browser offline
- [ ] Cached resources load → from IndexedDB
- [ ] Quiz offline → answers saved locally
- [ ] On reconnect → auto-sync pending actions

## Integration Testing

### API Endpoint Testing (Postman/curl)

```bash
# Register student
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "user": {"username": "testuser", "email": "test@test.com", "password": "pass"},
    "grade": 5
  }'

# Login
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "pass"}'

# Get dashboard (with token)
curl -X GET http://localhost:8000/api/users/dashboard/ \
  -H "Authorization: Bearer <token>"

# List quizzes
curl -X GET "http://localhost:8000/api/quizzes/?grade=5&subject=Maths"

# Submit quiz
curl -X POST http://localhost:8000/api/quizzes/<id>/submit/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"answers": {"0": "b", "1": "true"}}'
```

### WebSocket Testing

```bash
# Test doubt session WebSocket (if implemented)
wscat -c "ws://localhost:8000/ws/doubts/<session_id>/?token=<token>"
# Type: {"message": "test message"}
```

## Performance Testing

### Load Testing with Locust

```bash
pip install locust

# Create locustfile.py
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class UserBehavior(HttpUser):
    wait_time = between(1, 3)

    @task
    def list_quizzes(self):
        self.client.get("/api/quizzes/?grade=5")

    @task
    def dashboard(self):
        self.client.get("/api/users/dashboard/")
EOF

# Run load test
locust -f locustfile.py --host=http://localhost:8000
# Visit http://localhost:8089
```

### Database Query Performance

```bash
# Check query count
docker-compose exec backend python manage.py shell
>>> from django.test.utils import CaptureQueriesContext
>>> from django.db import connection
>>> with CaptureQueriesContext(connection) as ctx:
...     list(Quiz.objects.all())
... 
>>> print(f"Queries: {len(ctx)}")
>>> for q in ctx: print(q['sql'][:100])
```

## Continuous Integration (GitHub Actions)

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11

      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt

      - name: Run migrations
        run: |
          cd backend
          python manage.py migrate

      - name: Run tests
        run: |
          cd backend
          python manage.py test

      - name: Lint
        run: |
          pip install flake8
          flake8 backend --max-line-length=100
```

## Test Coverage Goals

- Backend: >= 80% code coverage
- Critical paths: 100% coverage
  - Authentication
  - Quiz grading
  - Admin actions

Current coverage: Run `coverage report` after tests

## Debugging Failed Tests

```bash
# Run with verbose output
docker-compose exec backend python manage.py test -v 2

# Drop into Python debugger
# Add to test: import pdb; pdb.set_trace()

# Run single test class
docker-compose exec backend python manage.py test users.tests.UserAuthenticationTestCase

# Run single test method
docker-compose exec backend python manage.py test users.tests.UserAuthenticationTestCase.test_login_success

# Keep database after failed test (for inspection)
docker-compose exec backend python manage.py test --keepdb
```

## Security Testing

```bash
# Django security checks
docker-compose exec backend python manage.py check --deploy

# SQL injection test
# POST /api/quizzes/?subject='; DROP TABLE quizzes; --

# CSRF protection
# Remove CSRF token and POST — should fail

# XSS test
# Upload resource with title: <script>alert('xss')</script>
# Should be escaped in response

# Rate limiting
# Send 100 requests in 1 second — should be throttled
```

## Reporting

Test results are saved to:
- `coverage.html` — line-by-line coverage
- `test_results.xml` — JUnit format for CI
- `.coverage` — coverage database

View coverage:
```bash
docker-compose exec backend coverage html
open htmlcov/index.html
```
