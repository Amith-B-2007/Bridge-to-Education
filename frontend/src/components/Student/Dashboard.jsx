import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { offlineManager } from '../../utils/offline';
import api from '../../utils/api';

export const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    fetchDashboard();
    offlineManager.addListener(setIsOnline);
  }, []);

  const fetchDashboard = async () => {
    try {
      const response = await api.get('/users/dashboard/');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', backgroundColor: '#f5f5f5'}}>
        <div style={{textAlign: 'center'}}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '3px solid #ddd',
            borderTop: '3px solid #00a8e8',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto'
          }}></div>
          <p style={{marginTop: '16px', color: '#666'}}>Loading...</p>
        </div>
      </div>
    );
  }

  const subjects = ['Kannada', 'English', 'Maths', 'Science', 'Social Science'];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div style={{minHeight: '100vh', backgroundColor: '#f5f5f5'}}>
      {/* Simple Header */}
      <header style={{backgroundColor: '#fff', borderBottom: '1px solid #eee', padding: '16px 0'}}>
        <div style={{maxWidth: '1200px', margin: '0 auto', padding: '0 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <div>
            <h1 style={{fontSize: '1.5rem', fontWeight: 700, color: '#0f3460'}}>RuralSiksha</h1>
            <p style={{color: '#666', fontSize: '0.9rem', marginTop: '4px'}}>Welcome, {user?.username || 'Student'}</p>
          </div>
          <button
            onClick={handleLogout}
            style={{
              padding: '8px 16px',
              backgroundColor: '#f5f5f5',
              border: '1px solid #ddd',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.9rem',
              fontWeight: 500,
              color: '#333',
              transition: 'background-color 0.2s'
            }}
            onMouseEnter={(e) => e.target.style.backgroundColor = '#eee'}
            onMouseLeave={(e) => e.target.style.backgroundColor = '#f5f5f5'}
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main style={{maxWidth: '1200px', margin: '0 auto', padding: '32px 20px'}}>
        {/* Quick Stats */}
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '32px'}}>
          <div style={{backgroundColor: '#fff', padding: '20px', borderRadius: '8px', border: '1px solid #eee'}}>
            <p style={{color: '#666', fontSize: '0.9rem', marginBottom: '12px'}}>Your Grade</p>
            <p style={{fontSize: '2.5rem', fontWeight: 700, color: '#0f3460'}}>
              {dashboardData?.student?.grade || user?.grade || '-'}
            </p>
          </div>
          <div style={{backgroundColor: '#fff', padding: '20px', borderRadius: '8px', border: '1px solid #eee'}}>
            <p style={{color: '#666', fontSize: '0.9rem', marginBottom: '12px'}}>Quizzes Taken</p>
            <p style={{fontSize: '2.5rem', fontWeight: 700, color: '#00a8e8'}}>
              {dashboardData?.total_quiz_attempts || 0}
            </p>
          </div>
          <div style={{backgroundColor: '#fff', padding: '20px', borderRadius: '8px', border: '1px solid #eee'}}>
            <p style={{color: '#666', fontSize: '0.9rem', marginBottom: '12px'}}>AI Sessions</p>
            <p style={{fontSize: '2.5rem', fontWeight: 700, color: '#00a8e8'}}>
              {dashboardData?.ai_tutor_sessions || 0}
            </p>
          </div>
        </div>

        {/* Main Actions */}
        <div style={{marginBottom: '32px'}}>
          <h2 style={{fontSize: '1.3rem', fontWeight: 700, color: '#0f3460', marginBottom: '16px'}}>What do you want to do?</h2>
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px'}}>
            <button
              onClick={() => navigate('/tutor')}
              style={{
                padding: '16px 20px',
                backgroundColor: '#fff',
                border: '1px solid #eee',
                borderRadius: '8px',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f9f9f9';
                e.currentTarget.style.borderColor = '#ddd';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#fff';
                e.currentTarget.style.borderColor = '#eee';
              }}
            >
              <p style={{fontSize: '1.4rem', marginBottom: '8px'}}>🤖</p>
              <p style={{fontWeight: 600, color: '#333', fontSize: '0.95rem'}}>Ask the AI Tutor</p>
              <p style={{fontSize: '0.85rem', color: '#666', marginTop: '4px'}}>Get help anytime</p>
            </button>

            <button
              onClick={() => navigate('/resources')}
              style={{
                padding: '16px 20px',
                backgroundColor: '#fff',
                border: '1px solid #eee',
                borderRadius: '8px',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f9f9f9';
                e.currentTarget.style.borderColor = '#ddd';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#fff';
                e.currentTarget.style.borderColor = '#eee';
              }}
            >
              <p style={{fontSize: '1.4rem', marginBottom: '8px'}}>📚</p>
              <p style={{fontWeight: 600, color: '#333', fontSize: '0.95rem'}}>Browse Resources</p>
              <p style={{fontSize: '0.85rem', color: '#666', marginTop: '4px'}}>Lessons & notes</p>
            </button>

            <button
              onClick={() => navigate('/quizzes')}
              style={{
                padding: '16px 20px',
                backgroundColor: '#fff',
                border: '1px solid #eee',
                borderRadius: '8px',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f9f9f9';
                e.currentTarget.style.borderColor = '#ddd';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#fff';
                e.currentTarget.style.borderColor = '#eee';
              }}
            >
              <p style={{fontSize: '1.4rem', marginBottom: '8px'}}>📝</p>
              <p style={{fontWeight: 600, color: '#333', fontSize: '0.95rem'}}>Take a Quiz</p>
              <p style={{fontSize: '0.85rem', color: '#666', marginTop: '4px'}}>Test yourself</p>
            </button>

            <button
              onClick={() => navigate('/doubts')}
              style={{
                padding: '16px 20px',
                backgroundColor: '#fff',
                border: '1px solid #eee',
                borderRadius: '8px',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f9f9f9';
                e.currentTarget.style.borderColor = '#ddd';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#fff';
                e.currentTarget.style.borderColor = '#eee';
              }}
            >
              <p style={{fontSize: '1.4rem', marginBottom: '8px'}}>💬</p>
              <p style={{fontWeight: 600, color: '#333', fontSize: '0.95rem'}}>Ask a Teacher</p>
              <p style={{fontSize: '0.85rem', color: '#666', marginTop: '4px'}}>Get real-time help</p>
            </button>
          </div>
        </div>

        {/* Subject Progress */}
        <div>
          <h2 style={{fontSize: '1.3rem', fontWeight: 700, color: '#0f3460', marginBottom: '16px'}}>Your Progress</h2>
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px'}}>
            {subjects.map((subject) => {
              const data = dashboardData?.subjects?.[subject] || { avg_score: 0 };
              return (
                <div key={subject} style={{
                  backgroundColor: '#fff',
                  padding: '16px',
                  borderRadius: '8px',
                  border: '1px solid #eee'
                }}>
                  <p style={{fontWeight: 600, color: '#333', marginBottom: '12px'}}>{subject}</p>
                  <p style={{fontSize: '1.8rem', fontWeight: 700, color: '#00a8e8', marginBottom: '8px'}}>
                    {data.avg_score}%
                  </p>
                  <div style={{
                    width: '100%',
                    height: '6px',
                    backgroundColor: '#eee',
                    borderRadius: '3px',
                    overflow: 'hidden'
                  }}>
                    <div
                      style={{
                        height: '100%',
                        backgroundColor: '#00a8e8',
                        width: `${data.avg_score}%`,
                        transition: 'width 0.3s'
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Offline Mode Banner */}
        {!isOnline && (
          <div style={{
            marginTop: '32px',
            padding: '16px 20px',
            backgroundColor: '#fff3cd',
            border: '1px solid #ffc107',
            borderRadius: '8px'
          }}>
            <p style={{color: '#856404', fontWeight: 600, marginBottom: '12px'}}>📴 You're currently offline</p>
            <p style={{color: '#856404', fontSize: '0.9rem', marginBottom: '12px'}}>
              You can still access cached resources and quizzes
            </p>
            <button
              onClick={() => navigate('/offline/resources')}
              style={{
                padding: '8px 16px',
                backgroundColor: '#ffc107',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: 500,
                color: '#000',
                marginRight: '8px',
                fontSize: '0.9rem'
              }}
            >
              Browse Offline Resources
            </button>
          </div>
        )}
      </main>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
