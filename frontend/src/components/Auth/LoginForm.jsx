import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const LoginForm = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex" style={{backgroundColor: '#f5f5f5'}}>
      {/* Left Side - Branding */}
      <div className="hidden lg:flex w-1/2" style={{backgroundColor: '#0f3460'}}>
        <div className="flex flex-col justify-center items-start w-full px-16">
          <h1 style={{color: '#00a8e8', fontSize: '2.5rem', fontWeight: 800, marginBottom: '16px'}}>
            RuralSiksha
          </h1>
          <p style={{color: '#ffffff', fontSize: '1.3rem', lineHeight: 1.6, marginBottom: '40px', maxWidth: '400px'}}>
            Empowering rural learners with AI-powered education and quality learning resources.
          </p>
          <div style={{color: '#888'}}>
            <p style={{marginBottom: '20px', fontSize: '0.95rem'}}>✓ 24/7 AI Tutoring</p>
            <p style={{marginBottom: '20px', fontSize: '0.95rem'}}>✓ Real-time Doubt Support</p>
            <p style={{marginBottom: '20px', fontSize: '0.95rem'}}>✓ Comprehensive Resources</p>
            <p style={{marginBottom: '20px', fontSize: '0.95rem'}}>✓ Offline Learning Mode</p>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center px-4 py-12">
        <div style={{width: '100%', maxWidth: '420px'}}>
          <div style={{marginBottom: '32px'}}>
            <h2 style={{fontSize: '1.875rem', fontWeight: 700, color: '#0f3460', marginBottom: '8px'}}>
              Welcome Back
            </h2>
            <p style={{color: '#666', fontSize: '0.95rem'}}>
              Sign in to your account to continue learning
            </p>
          </div>

          {error && (
            <div style={{
              marginBottom: '20px',
              padding: '12px 16px',
              backgroundColor: '#fee',
              border: '1px solid #fcc',
              borderRadius: '6px',
              color: '#c33',
              fontSize: '0.9rem'
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div style={{marginBottom: '20px'}}>
              <label style={{
                display: 'block',
                fontSize: '0.9rem',
                fontWeight: 600,
                color: '#333',
                marginBottom: '8px'
              }}>
                Username or Email
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '0.95rem',
                  fontFamily: 'inherit',
                  boxSizing: 'border-box',
                  transition: 'border-color 0.2s'
                }}
                placeholder="your.username@email.com"
                required
                onFocus={(e) => e.target.style.borderColor = '#00a8e8'}
                onBlur={(e) => e.target.style.borderColor = '#ddd'}
              />
            </div>

            <div style={{marginBottom: '28px'}}>
              <label style={{
                display: 'block',
                fontSize: '0.9rem',
                fontWeight: 600,
                color: '#333',
                marginBottom: '8px'
              }}>
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '0.95rem',
                  fontFamily: 'inherit',
                  boxSizing: 'border-box',
                  transition: 'border-color 0.2s'
                }}
                placeholder="••••••••"
                required
                onFocus={(e) => e.target.style.borderColor = '#00a8e8'}
                onBlur={(e) => e.target.style.borderColor = '#ddd'}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '11px 16px',
                backgroundColor: loading ? '#999' : '#00a8e8',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '0.95rem',
                fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'background-color 0.2s',
                marginBottom: '16px'
              }}
              onMouseEnter={(e) => !loading && (e.target.style.backgroundColor = '#0084d1')}
              onMouseLeave={(e) => !loading && (e.target.style.backgroundColor = '#00a8e8')}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div style={{
            textAlign: 'center',
            paddingTop: '16px',
            borderTop: '1px solid #eee'
          }}>
            <p style={{color: '#666', fontSize: '0.9rem'}}>
              Don't have an account?{' '}
              <Link to="/register" style={{
                color: '#00a8e8',
                textDecoration: 'none',
                fontWeight: 600
              }}>
                Create one here
              </Link>
            </p>
          </div>

          <div style={{marginTop: '32px', paddingTop: '20px', borderTop: '1px solid #eee', textAlign: 'center'}}>
            <p style={{color: '#999', fontSize: '0.85rem', marginBottom: '8px'}}>Demo Credentials:</p>
            <p style={{color: '#999', fontSize: '0.85rem'}}>Username: demo | Password: demo123</p>
          </div>
        </div>
      </div>
    </div>
  );
};
