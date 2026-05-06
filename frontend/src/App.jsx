import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { PrivateRoute } from './components/Auth/PrivateRoute';
import { LoginForm } from './components/Auth/LoginForm';
import { RegisterForm } from './components/Auth/RegisterForm';
import { Dashboard } from './components/Student/Dashboard';
import { AITutor } from './components/Student/AITutor';
import { ResourceBrowser } from './components/Student/ResourceBrowser';
import { QuizModule } from './components/Student/QuizModule';
import { DoubtChat } from './components/Student/DoubtChat';
import { OfflineIndicator } from './components/Student/OfflineIndicator';
import { OfflineResourceBrowser } from './components/Student/OfflineResourceBrowser';
import { OfflineQuizTaker } from './components/Student/OfflineQuizTaker';
import { TeacherDashboard } from './components/Teacher/TeacherDashboard';
import { MentorDashboard } from './components/Mentor/MentorDashboard';
import { AdminDashboard } from './components/Admin/AdminDashboard';
import './App.css';

function ProfessionalHomePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Professional Header/Navigation */}
      <header className="prof-header">
        <div className="prof-container flex justify-between items-center py-4">
          <div>
            <h1>RuralSiksha</h1>
            <p>Transforming Education in Rural India</p>
          </div>
          <nav className="prof-nav">
            <a href="#features">Features</a>
            <a href="#about">About</a>
            <a href="/login" className="prof-button">Login</a>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="prof-hero">
        <div className="prof-container">
          <h1>Quality Education for Every Student</h1>
          <p>Empowering rural learners with AI-powered tutoring, interactive resources, and real-time support from experienced educators.</p>
          <div className="prof-hero-buttons">
            <a href="/register" className="prof-button">Get Started</a>
            <a href="#features" className="prof-button prof-button-secondary">Learn More</a>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="prof-section" id="features">
        <div className="prof-container">
          <h2 className="prof-section-title">Why Choose RuralSiksha?</h2>
          <p className="prof-section-subtitle">A comprehensive platform designed for student success</p>
          
          <div className="prof-grid-3">
            <div className="prof-card">
              <div className="prof-card-icon">🤖</div>
              <h3>AI-Powered Tutoring</h3>
              <p>24/7 personalized learning assistance powered by advanced AI that adapts to your learning pace and style.</p>
            </div>

            <div className="prof-card">
              <div className="prof-card-icon">📚</div>
              <h3>Rich Learning Resources</h3>
              <p>Access comprehensive lessons, PDFs, videos, and interactive content curated by expert educators.</p>
            </div>

            <div className="prof-card">
              <div className="prof-card-icon">📝</div>
              <h3>Smart Assessment</h3>
              <p>Subject and chapter-wise quizzes with instant feedback to track your progress effectively.</p>
            </div>

            <div className="prof-card">
              <div className="prof-card-icon">💬</div>
              <h3>Real-Time Support</h3>
              <p>Connect with expert teachers and mentors instantly for doubt clarification and personalized guidance.</p>
            </div>

            <div className="prof-card">
              <div className="prof-card-icon">📊</div>
              <h3>Progress Analytics</h3>
              <p>Track your performance with detailed analytics and actionable insights to improve your academic outcomes.</p>
            </div>

            <div className="prof-card">
              <div className="prof-card-icon">🔌</div>
              <h3>Offline Access</h3>
              <p>Download resources and take quizzes offline - perfect for areas with limited internet connectivity.</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="prof-section" style={{backgroundColor: '#f8f9fa'}}>
        <div className="prof-container">
          <h2 className="prof-section-title">How It Works</h2>
          <p className="prof-section-subtitle">Get started in three simple steps</p>
          
          <div className="prof-grid-3">
            <div style={{textAlign: 'center'}}>
              <div style={{
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #00a8e8 0%, #0084d1 100%)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '28px',
                margin: '0 auto 20px',
                fontWeight: 'bold'
              }}>1</div>
              <h3 style={{color: '#0f3460', fontWeight: 700, marginBottom: '12px'}}>Sign Up</h3>
              <p style={{color: '#666'}}>Create your account and choose your grade and subjects of interest.</p>
            </div>

            <div style={{textAlign: 'center'}}>
              <div style={{
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #00a8e8 0%, #0084d1 100%)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '28px',
                margin: '0 auto 20px',
                fontWeight: 'bold'
              }}>2</div>
              <h3 style={{color: '#0f3460', fontWeight: 700, marginBottom: '12px'}}>Learn & Practice</h3>
              <p style={{color: '#666'}}>Access resources, interact with the AI tutor, and solve quizzes.</p>
            </div>

            <div style={{textAlign: 'center'}}>
              <div style={{
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #00a8e8 0%, #0084d1 100%)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '28px',
                margin: '0 auto 20px',
                fontWeight: 'bold'
              }}>3</div>
              <h3 style={{color: '#0f3460', fontWeight: 700, marginBottom: '12px'}}>Track Progress</h3>
              <p style={{color: '#666'}}>Monitor your performance and get personalized recommendations.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Statistics Section */}
      <section className="prof-section" style={{backgroundColor: '#0f3460', color: 'white'}}>
        <div className="prof-container">
          <h2 className="prof-section-title" style={{color: 'white'}}>Our Impact</h2>
          
          <div className="prof-grid-3" style={{marginTop: '40px'}}>
            <div className="prof-stat">
              <div className="prof-stat-number" style={{color: '#00d4ff'}}>15,000+</div>
              <div className="prof-stat-label">Active Students</div>
            </div>

            <div className="prof-stat">
              <div className="prof-stat-number" style={{color: '#00d4ff'}}>500+</div>
              <div className="prof-stat-label">Experienced Educators</div>
            </div>

            <div className="prof-stat">
              <div className="prof-stat-number" style={{color: '#00d4ff'}}>95%</div>
              <div className="prof-stat-label">Student Success Rate</div>
            </div>
          </div>
        </div>
      </section>

      {/* For Different User Types */}
      <section className="prof-section">
        <div className="prof-container">
          <h2 className="prof-section-title">For Everyone</h2>
          <p className="prof-section-subtitle">Tailored features for students, teachers, and parents</p>
          
          <div className="prof-grid-2">
            <div>
              <h3 style={{color: '#0f3460', fontSize: '1.5rem', fontWeight: 700, marginBottom: '20px'}}>👨‍🎓 For Students</h3>
              <ul className="prof-feature-list">
                <li>24/7 AI tutoring assistance</li>
                <li>Comprehensive learning resources</li>
                <li>Interactive quizzes and assessments</li>
                <li>Real-time doubt clarification</li>
                <li>Offline learning capability</li>
                <li>Detailed progress tracking</li>
              </ul>
            </div>
            <div>
              <h3 style={{color: '#0f3460', fontSize: '1.5rem', fontWeight: 700, marginBottom: '20px'}}>👨‍🏫 For Teachers</h3>
              <ul className="prof-feature-list">
                <li>Respond to student doubts in real-time</li>
                <li>Upload and manage resources</li>
                <li>Track student performance</li>
                <li>Manage grades and marks</li>
                <li>Monitor class progress</li>
                <li>Generate performance reports</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="prof-section" style={{backgroundColor: 'linear-gradient(135deg, #0f3460 0%, #16213e 100%)', color: 'white', textAlign: 'center'}}>
        <div className="prof-container">
          <h2 style={{fontSize: '2.2rem', fontWeight: 800, marginBottom: '16px'}}>Ready to Transform Your Learning?</h2>
          <p style={{fontSize: '1.1rem', marginBottom: '30px', maxWidth: '600px', marginLeft: 'auto', marginRight: 'auto'}}>
            Join thousands of students already benefiting from RuralSiksha's comprehensive learning platform.
          </p>
          <div style={{display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap'}}>
            <a href="/register" className="prof-button">Sign Up Now</a>
            <a href="/login" className="prof-button prof-button-secondary" style={{borderColor: 'white', color: 'white'}}>Login</a>
          </div>
        </div>
      </section>

      {/* Professional Footer */}
      <footer className="prof-footer">
        <div className="prof-container">
          <p style={{fontSize: '1.1rem', fontWeight: 600, marginBottom: '8px'}}>RuralSiksha</p>
          <p>Empowering Rural Education Through Technology</p>
          <p style={{marginTop: '20px', fontSize: '0.9rem', opacity: 0.8}}>© 2026 RuralSiksha. All rights reserved. | Connecting Rural Students with Quality Education</p>
        </div>
      </footer>
    </div>
  );
}

function OfflineResourcesPage() {
  const { user } = useAuth();
  return (
    <div className="prof-page-shell">
      <header className="prof-page-header">
        <div className="prof-page-header-inner">
          <div>
            <h1 className="prof-page-title">📦 Offline Resources</h1>
            <p className="prof-page-subtitle">Cached learning materials available without internet</p>
          </div>
          <a href="/dashboard" className="text-cyan-300 hover:text-cyan-200 font-semibold">← Dashboard</a>
        </div>
      </header>
      <main className="prof-main">
        <OfflineResourceBrowser grade={user?.grade || 1} subject="Maths" />
      </main>
    </div>
  );
}

function OfflineQuizPage() {
  const [selectedQuizId, setSelectedQuizId] = useState(null);

  if (selectedQuizId) {
    return (
      <div className="prof-page-shell" style={{ padding: 24 }}>
        <OfflineQuizTaker
          quizId={selectedQuizId}
          onComplete={() => setSelectedQuizId(null)}
        />
      </div>
    );
  }

  return (
    <div className="prof-page-shell">
      <header className="prof-page-header">
        <div className="prof-page-header-inner">
          <div>
            <h1 className="prof-page-title">📋 Offline Quizzes</h1>
            <p className="prof-page-subtitle">Take cached quizzes anytime, no internet required</p>
          </div>
          <a href="/dashboard" className="text-cyan-300 hover:text-cyan-200 font-semibold">← Dashboard</a>
        </div>
      </header>
      <main className="prof-main">
        <div className="prof-surface" style={{ padding: 48, textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: 12 }}>📥</div>
          <p style={{ color: '#475569', fontSize: 16, marginBottom: 8 }}>
            Select a cached quiz to take offline
          </p>
          <p style={{ color: '#94a3b8', fontSize: 14 }}>
            Download quizzes while online to use this feature
          </p>
        </div>
      </main>
    </div>
  );
}

function RoleBasedDashboard() {
  const { user } = useAuth();
  if (user?.role === 'teacher') return <TeacherDashboard />;
  if (user?.role === 'mentor') return <MentorDashboard />;
  if (user?.role === 'admin') return <AdminDashboard />;
  return <Dashboard />;
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <OfflineIndicator />
        <Routes>
          <Route path="/" element={<ProfessionalHomePage />} />
          <Route path="/login" element={<LoginForm />} />
          <Route path="/register" element={<RegisterForm />} />

          <Route path="/dashboard" element={<PrivateRoute><RoleBasedDashboard /></PrivateRoute>} />
          <Route path="/tutor" element={<PrivateRoute><AITutor /></PrivateRoute>} />
          <Route path="/resources" element={<PrivateRoute><ResourceBrowser /></PrivateRoute>} />
          <Route path="/quizzes" element={<PrivateRoute><QuizModule /></PrivateRoute>} />
          <Route path="/doubts" element={<PrivateRoute><DoubtChat /></PrivateRoute>} />

          <Route path="/teacher" element={<PrivateRoute><TeacherDashboard /></PrivateRoute>} />
          <Route path="/mentor" element={<PrivateRoute><MentorDashboard /></PrivateRoute>} />
          <Route path="/admin-portal" element={<PrivateRoute><AdminDashboard /></PrivateRoute>} />

          <Route path="/offline/resources" element={<PrivateRoute><OfflineResourcesPage /></PrivateRoute>} />
          <Route path="/offline/quiz" element={<PrivateRoute><OfflineQuizPage /></PrivateRoute>} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
