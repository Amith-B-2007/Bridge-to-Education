import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const RegisterForm = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    school_name: '',
    role: 'student',
    password: '',
    password_confirm: '',
    grade: '1',
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (formData.password !== formData.password_confirm) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      const userData = {
        user: {
          username: formData.username,
          email: formData.email,
          first_name: formData.first_name,
          last_name: formData.last_name,
          phone: formData.phone || null,
          school_name: formData.school_name || null,
        },
        password: formData.password,
        password_confirm: formData.password_confirm,
        role: formData.role,
      };

      if (formData.role === 'student') {
        userData.grade = parseInt(formData.grade);
      }

      await register(userData);
      navigate('/dashboard');
    } catch (err) {
      console.error('Registration error:', err);
      // Get detailed error message
      let errorMsg = 'Registration failed';
      if (err.response?.data) {
        const data = err.response.data;
        if (typeof data === 'object') {
          // Handle nested errors
          if (data.user) {
            const userErrors = Object.values(data.user).flat();
            errorMsg = userErrors.join(', ');
          } else if (data.detail) {
            errorMsg = data.detail;
          } else {
            errorMsg = Object.values(data).flat().join(', ');
          }
        }
      }
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    width: '100%',
    padding: '10px 12px',
    border: '1px solid #ddd',
    borderRadius: '6px',
    fontSize: '0.95rem',
    fontFamily: 'inherit',
    boxSizing: 'border-box',
    transition: 'border-color 0.2s'
  };

  return (
    <div style={{minHeight: '100vh', display: 'flex', backgroundColor: '#f5f5f5', paddingTop: '24px', paddingBottom: '24px'}}>
      {/* Left Side - Branding */}
      <div style={{display: 'none', width: '50%', backgroundColor: '#0f3460', '@media (min-width: 1024px)': {display: 'flex'}}}>
        <div style={{display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'flex-start', width: '100%', paddingLeft: '64px', paddingRight: '64px'}}>
          <h1 style={{color: '#00a8e8', fontSize: '2.5rem', fontWeight: 800, marginBottom: '16px'}}>
            Join RuralSiksha
          </h1>
          <p style={{color: '#ffffff', fontSize: '1.1rem', lineHeight: 1.6, marginBottom: '40px', maxWidth: '400px'}}>
            Start your learning journey today and unlock access to quality education resources.
          </p>
          <div style={{color: '#888'}}>
            <p style={{marginBottom: '20px', fontSize: '0.95rem'}}>✓ Free educational resources</p>
            <p style={{marginBottom: '20px', fontSize: '0.95rem'}}>✓ AI-powered tutoring support</p>
            <p style={{marginBottom: '20px', fontSize: '0.95rem'}}>✓ Real-time doubt resolution</p>
            <p style={{marginBottom: '20px', fontSize: '0.95rem'}}>✓ Offline learning capability</p>
          </div>
        </div>
      </div>

      {/* Right Side - Registration Form */}
      <div style={{width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', paddingLeft: '16px', paddingRight: '16px'}}>
        <div style={{width: '100%', maxWidth: '420px'}}>
          <div style={{marginBottom: '32px'}}>
            <h2 style={{fontSize: '1.875rem', fontWeight: 700, color: '#0f3460', marginBottom: '8px'}}>
              Create Account
            </h2>
            <p style={{color: '#666', fontSize: '0.95rem'}}>
              Fill in your details to get started
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

          <form onSubmit={handleSubmit} style={{display: 'grid', gap: '16px'}}>
            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px'}}>
              <div>
                <label style={{display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#333', marginBottom: '6px'}}>
                  First Name *
                </label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  style={inputStyle}
                  placeholder="John"
                  required
                  onFocus={(e) => e.target.style.borderColor = '#00a8e8'}
                  onBlur={(e) => e.target.style.borderColor = '#ddd'}
                />
              </div>
              <div>
                <label style={{display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#333', marginBottom: '6px'}}>
                  Last Name *
                </label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  style={inputStyle}
                  placeholder="Doe"
                  required
                  onFocus={(e) => e.target.style.borderColor = '#00a8e8'}
                  onBlur={(e) => e.target.style.borderColor = '#ddd'}
                />
              </div>
            </div>

            <div>
              <label style={{display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#333', marginBottom: '6px'}}>
                Username *
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                style={inputStyle}
                placeholder="johndoe"
                required
                onFocus={(e) => e.target.style.borderColor = '#00a8e8'}
                onBlur={(e) => e.target.style.borderColor = '#ddd'}
              />
            </div>

            <div>
              <label style={{display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#333', marginBottom: '6px'}}>
                Email *
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                style={inputStyle}
                placeholder="john@example.com"
                required
                onFocus={(e) => e.target.style.borderColor = '#00a8e8'}
                onBlur={(e) => e.target.style.borderColor = '#ddd'}
              />
            </div>

            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px'}}>
              <div>
                <label style={{display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#333', marginBottom: '6px'}}>
                  Phone
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  style={inputStyle}
                  placeholder="+91 9876543210"
                  onFocus={(e) => e.target.style.borderColor = '#00a8e8'}
                  onBlur={(e) => e.target.style.borderColor = '#ddd'}
                />
              </div>
              <div>
                <label style={{display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#333', marginBottom: '6px'}}>
                  Role *
                </label>
                <select
                  name="role"
                  value={formData.role}
                  onChange={handleChange}
                  style={{...inputStyle, cursor: 'pointer'}}
                  onFocus={(e) => e.target.style.borderColor = '#00a8e8'}
                  onBlur={(e) => e.target.style.borderColor = '#ddd'}
                >
                  <option value="student">Student</option>
                  <option value="teacher">Teacher</option>
                </select>
              </div>
            </div>

            <div>
              <label style={{display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#333', marginBottom: '6px'}}>
                School Name
              </label>
              <input
                type="text"
                name="school_name"
                value={formData.school_name}
                onChange={handleChange}
                style={inputStyle}
                placeholder="Your School"
                onFocus={(e) => e.target.style.borderColor = '#00a8e8'}
                onBlur={(e) => e.target.style.borderColor = '#ddd'}
              />
            </div>

            {formData.role === 'student' && (
              <div>
                <label style={{display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#333', marginBottom: '6px'}}>
                  Grade *
                </label>
                <select
                  name="grade"
                  value={formData.grade}
                  onChange={handleChange}
                  style={{...inputStyle, cursor: 'pointer'}}
                  onFocus={(e) => e.target.style.borderColor = '#00a8e8'}
                  onBlur={(e) => e.target.style.borderColor = '#ddd'}
                >
                  {Array.from({ length: 10 }, (_, i) => (
                    <option key={i + 1} value={i + 1}>
                      Grade {i + 1}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div>
              <label style={{display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#333', marginBottom: '6px'}}>
                Password *
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                style={inputStyle}
                placeholder="••••••••"
                required
                onFocus={(e) => e.target.style.borderColor = '#00a8e8'}
                onBlur={(e) => e.target.style.borderColor = '#ddd'}
              />
            </div>

            <div>
              <label style={{display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#333', marginBottom: '6px'}}>
                Confirm Password *
              </label>
              <input
                type="password"
                name="password_confirm"
                value={formData.password_confirm}
                onChange={handleChange}
                style={inputStyle}
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
                marginTop: '8px'
              }}
              onMouseEnter={(e) => !loading && (e.target.style.backgroundColor = '#0084d1')}
              onMouseLeave={(e) => !loading && (e.target.style.backgroundColor = '#00a8e8')}
            >
              {loading ? 'Creating Account...' : 'Sign Up'}
            </button>
          </form>

          <div style={{
            textAlign: 'center',
            paddingTop: '16px',
            borderTop: '1px solid #eee',
            marginTop: '24px'
          }}>
            <p style={{color: '#666', fontSize: '0.9rem'}}>
              Already have an account?{' '}
              <Link to="/login" style={{
                color: '#00a8e8',
                textDecoration: 'none',
                fontWeight: 600
              }}>
                Sign in here
              </Link>
            </p>
          </div>
        </div>
      </div>

      <style>{`
        @media (min-width: 1024px) {
          div[style*="display: none"] {
            display: flex !important;
          }
        }
      `}</style>
    </div>
  );
};
