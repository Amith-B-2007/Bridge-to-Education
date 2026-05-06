# How to Run RuralShiksha Locally

This guide is for running the project **on your own Windows machine** — no Docker, no Claude preview required.

## Prerequisites

Make sure you have these installed:

1. **Python 3.10+** — https://www.python.org/downloads/
   - During install, check "Add Python to PATH"
2. **Node.js 18+** — https://nodejs.org/

Verify in a terminal:
```
python --version
node --version
npm --version
```

## First-Time Setup

Open a Command Prompt or PowerShell in this folder, then run:

```
setup.bat
```

This will:
- Install all Python dependencies (`Django`, `DRF`, `JWT`, etc.)
- Run database migrations
- Create demo users
- Install all Node.js dependencies (`React`, `Vite`, `Tailwind`)

## Starting the Project

After setup completes, just run:

```
start.bat
```

This opens **two separate terminal windows**:
- **Backend** — Django on http://localhost:8000
- **Frontend** — Vite/React on http://localhost:5173

Then open your browser at: **http://localhost:5173**

## Demo Credentials

| Username | Password | Role |
|----------|----------|------|
| `demo` | `demo123` | Student |
| `teacher` | `teacher123` | Teacher |
| `admin` | `admin123` | Admin |

## Manual Run (if you don't want to use the .bat files)

### Terminal 1 - Backend
```
cd backend
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Terminal 2 - Frontend
```
cd frontend
npm install
npm run dev
```

## Stopping the Servers

In each terminal window, press `Ctrl + C`.

## Troubleshooting

### "python is not recognized"
- Reinstall Python and check "Add to PATH" during install.

### "npm is not recognized"
- Reinstall Node.js from nodejs.org.

### "Port already in use"
- Something else is using port 8000 or 5173. Either close that program or change the port:
  - Backend: `python manage.py runserver 0.0.0.0:8001`
  - Frontend: edit `frontend/vite.config.js` and change `server.port`

### "Login failed"
- Run `setup.bat` again to (re-)create the demo users.

### Database is empty / corrupted
- Delete `backend/db.sqlite3` and run `setup.bat` again.

## What's Included

- **Student Portal**: Dashboard, AI Tutor, Resources, Quizzes, Doubts
- **Teacher Portal**: Pending Doubts, Resource Upload, Marks Upload (with SMS hooks)
- **Mentor Portal**: Student progress tracking
- **Offline Mode**: Browse cached resources, take cached quizzes
- **PWA**: Service worker for offline support

## Optional: Real-Time WebSockets

The doubts chat works over REST API by default. To enable real-time WebSockets:

1. `pip install channels daphne`
2. Uncomment `'daphne'` and `'channels'` in `backend/ruralsiksha/settings.py` `INSTALLED_APPS`
3. Restore the `DoubtConsumer` class in `backend/doubts/consumers.py`
4. Add channel layers config back to `settings.py`

## Optional: SMS Notifications

To enable Fast2SMS notifications to parents:

1. Get an API key from https://www.fast2sms.com/
2. Set `FAST2SMS_API_KEY=your_key` in a `.env` file inside `backend/`

Without an API key, the SMS code logs the message but doesn't actually send.
