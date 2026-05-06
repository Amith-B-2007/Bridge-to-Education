# RuralShiksha - AI-Powered Educational Platform

A comprehensive educational platform designed specifically for rural students in Karnataka, with AI-powered tutoring, offline-first functionality, and real-time teacher interaction.

## 🎯 Features

### For Students
- **Dashboard**: Subject-wise progress tracking, quiz scores, attendance
- **AI Tutor**: Chat-based AI tutor (powered by Ollama) for curriculum-mapped learning
- **Resources**: Browse, download, and access lessons offline
- **Quizzes**: Subject and chapter-wise MCQ with instant auto-grading
- **Doubt Sessions**: Real-time chat with teachers for instant help
- **Offline Mode**: Full offline access to downloaded resources and quizzes

### For Teachers
- **Doubt Management**: Real-time answering of student questions
- **Resource Upload**: Upload lessons, PDFs, videos for specific grades/subjects
- **Marks Management**: Upload and track student marks
- **Class Management**: Monitor student progress and performance

### For Parents
- **SMS Notifications**: Get updates on quiz scores and marks
- **Progress Tracking**: Monitor child's academic progress
- **Customizable Alerts**: Choose which notifications to receive

## 📋 Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL (for production) or SQLite (for development)
- Ollama (for AI tutor features)
- Redis (for Celery task queue)

## 🚀 Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install

# Create .env file
cp .env.example .env

# Start development server
npm run dev
```

## 🏗️ Project Structure

```
RuralShiksha/
├── backend/
│   ├── users/               # Authentication & user management
│   ├── resources/           # Lesson materials, PDFs, videos
│   ├── quizzes/             # Quiz management & auto-grading
│   ├── ai_tutor/            # Ollama integration & chat
│   ├── doubts/              # Real-time teacher chat
│   ├── notifications/       # SMS & email notifications
│   └── ruralsiksha/         # Django config
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── context/         # State management
│   │   ├── utils/           # API client, helpers
│   │   └── pages/           # Page components
│   └── public/              # Static assets & PWA manifest
└── .env.example             # Environment variables template
```

## 🔧 Configuration

### Backend (.env)

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=llama3
FAST2SMS_API_KEY=your-api-key
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000/api
VITE_ENVIRONMENT=development
```

## 📡 API Endpoints

### Authentication
- `POST /api/users/register/` - Register new user
- `POST /api/users/login/` - Login and get JWT tokens
- `GET /api/users/profile/` - Get user profile
- `PUT /api/users/profile/` - Update profile

### Resources
- `GET /api/resources/subjects/` - List all subjects
- `GET /api/resources/chapters/` - List chapters by grade/subject
- `GET /api/resources/resources/` - Browse resources
- `POST /api/resources/resources/` - Upload resource (teacher only)

### Quizzes
- `GET /api/quizzes/` - List quizzes
- `POST /api/quizzes/{id}/submit/` - Submit quiz answers
- `GET /api/quizzes/my_attempts/` - Quiz history

### AI Tutor
- `POST /api/ai-tutor/sessions/` - Start new tutor session
- `POST /api/ai-tutor/sessions/{id}/send_message/` - Send message (streaming)

## 🧪 Testing

### Backend
```bash
cd backend
python manage.py test
```

### Frontend
```bash
cd frontend
npm test
```

## 📱 Offline Functionality

The app uses Service Workers and IndexedDB for offline access:
- Downloaded resources cached locally
- Quiz attempts saved offline
- Syncs when connection restored
- Offline indicator in UI

## 🔐 Security

- JWT-based authentication
- Role-based access control (Student, Teacher, Mentor, Parent)
- HTTPS enforced in production
- Environment variables for sensitive data
- SQL injection prevention via ORM

## 🚢 Deployment

### Production Deployment

```bash
# Backend (with Gunicorn + Nginx)
gunicorn ruralsiksha.wsgi:application --bind 0.0.0.0:8000

# Frontend (build)
npm run build
# Serve with Nginx or Vercel
```

## 📚 Documentation

- [Backend API Documentation](./backend/API_DOCS.md)
- [Database Schema](./backend/SCHEMA.md)
- [Deployment Guide](./DEPLOYMENT.md)

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit changes (`git commit -m 'Add amazing feature'`)
3. Push to branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙋 Support

For issues and questions:
- Open an issue on GitHub
- Email: support@ruralshiksha.in

## 🎓 Acknowledgments

- Karnataka State Board NCERT curriculum
- Ollama for open-source AI models
- Fast2SMS for SMS integration
- Tailwind CSS for styling
