import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';
import { ChatMessage } from './ChatMessage';

export const AITutor = () => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [subject, setSubject] = useState('Maths');
  const [language, setLanguage] = useState('en');
  const [showNewModal, setShowNewModal] = useState(false);
  const messagesEndRef = useRef(null);

  const subjects = ['Kannada', 'English', 'Maths', 'Science', 'Social Science'];

  useEffect(() => { fetchSessions(); }, []);
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchSessions = async () => {
    try {
      const response = await api.get('/ai-tutor/sessions/');
      const data = response.data.results || response.data || [];
      setSessions(data);
      if (data.length > 0 && !activeSession) {
        setActiveSession(data[0]);
        setMessages(data[0].messages || []);
      }
    } catch (error) {
      console.error('Error fetching sessions:', error);
    }
  };

  const createSession = async () => {
    try {
      const response = await api.post('/ai-tutor/sessions/', { subject, language });
      setActiveSession(response.data);
      setMessages([]);
      setSessions([response.data, ...sessions]);
      setShowNewModal(false);
    } catch (error) {
      console.error('Error creating session:', error);
      alert('Failed to create session');
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || !activeSession || streaming) return;

    const msg = inputMessage;
    setInputMessage('');
    setMessages(prev => [...prev, { role: 'student', content: msg, created_at: new Date().toISOString() }]);
    setStreaming(true);

    try {
      const url = `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/ai-tutor/sessions/${activeSession.id}/send_message/`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ message: msg }),
      });

      if (!response.ok || !response.body) {
        setMessages(prev => [...prev, {
          role: 'tutor',
          content: '(AI tutor service is not configured. Please ensure Ollama is running locally.)',
          created_at: new Date().toISOString(),
        }]);
        setStreaming(false);
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let full = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = decoder.decode(value);
        const lines = text.split('\n').filter(l => l.startsWith('data: '));
        for (const line of lines) {
          try {
            const json = JSON.parse(line.replace('data: ', ''));
            if (json.chunk) {
              full += json.chunk;
              setMessages(prev => {
                const last = prev[prev.length - 1];
                if (last?.role === 'tutor') {
                  return [...prev.slice(0, -1), { role: 'tutor', content: full, created_at: last.created_at }];
                }
                return [...prev, { role: 'tutor', content: full, created_at: new Date().toISOString() }];
              });
            }
          } catch (e) {}
        }
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setStreaming(false);
    }
  };

  return (
    <div className="prof-page-shell" style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <header className="prof-page-header">
        <div className="prof-page-header-inner">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="text-cyan-300 hover:text-cyan-200 font-semibold"
            >
              ← Back
            </button>
            <div>
              <h1 className="prof-page-title">🤖 AI Tutor</h1>
              <p className="prof-page-subtitle">Personalised learning assistance powered by AI</p>
            </div>
          </div>
        </div>
      </header>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden', background: '#f3f6fb' }}>
        <aside style={{
          width: 300,
          background: '#fff',
          borderRight: '1px solid #e5ebf3',
          display: 'flex',
          flexDirection: 'column',
        }}>
          <div style={{ padding: 16, borderBottom: '1px solid #e5ebf3' }}>
            <button
              onClick={() => setShowNewModal(true)}
              className="prof-action-btn prof-action-btn-primary"
              style={{ width: '100%', padding: '10px 14px' }}
            >
              + New Tutor Session
            </button>
          </div>
          <div style={{ flex: 1, overflowY: 'auto' }}>
            {sessions.length === 0 ? (
              <div style={{ padding: 16, color: '#64748b', fontSize: 14 }}>
                No sessions yet. Start one to chat with your tutor.
              </div>
            ) : (
              sessions.map(s => (
                <button
                  key={s.id}
                  onClick={() => { setActiveSession(s); setMessages(s.messages || []); }}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    padding: '14px 16px',
                    border: 'none',
                    borderBottom: '1px solid #f1f5f9',
                    background: activeSession?.id === s.id ? '#e0f6ff' : 'transparent',
                    borderLeft: activeSession?.id === s.id ? '4px solid #0084d1' : '4px solid transparent',
                    cursor: 'pointer',
                  }}
                >
                  <div style={{ fontWeight: 600, color: '#0f3460', fontSize: 14 }}>
                    {s.subject || 'General'}
                  </div>
                  <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>
                    {s.language === 'kn' ? '🌐 ಕನ್ನಡ' : '🌐 English'} · {s.message_count || 0} messages
                  </div>
                </button>
              ))
            )}
          </div>
        </aside>

        <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          {activeSession ? (
            <>
              <div style={{
                background: '#fff',
                borderBottom: '1px solid #e5ebf3',
                padding: '16px 24px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}>
                <div>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f3460' }}>
                    {activeSession.subject} Tutor
                  </h2>
                  <p style={{ fontSize: 13, color: '#64748b', marginTop: 2 }}>
                    Ask anything about your syllabus — get step-by-step answers
                  </p>
                </div>
                <span style={{
                  fontSize: 12,
                  background: '#e0f6ff',
                  color: '#0084d1',
                  padding: '6px 12px',
                  borderRadius: 999,
                  fontWeight: 600,
                }}>
                  {activeSession.language === 'kn' ? 'ಕನ್ನಡ' : 'English'}
                </span>
              </div>

              <div style={{ flex: 1, overflowY: 'auto', padding: 24, background: '#f3f6fb' }}>
                {messages.length === 0 ? (
                  <div style={{ textAlign: 'center', color: '#64748b', paddingTop: 80 }}>
                    <div style={{ fontSize: '3rem', marginBottom: 12 }}>👋</div>
                    <h3 style={{ fontWeight: 700, color: '#0f3460', fontSize: '1.2rem', marginBottom: 8 }}>
                      Welcome to your AI Tutor!
                    </h3>
                    <p>Ask any question about {activeSession.subject}.</p>
                    <p style={{ fontSize: 13, marginTop: 4 }}>
                      Example: "Explain quadratic equations with examples"
                    </p>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {messages.map((m, i) => <ChatMessage key={i} message={m} />)}
                    {streaming && (
                      <div style={{ color: '#64748b', fontSize: 13, fontStyle: 'italic' }}>
                        Tutor is thinking…
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>

              <form
                onSubmit={sendMessage}
                style={{
                  background: '#fff',
                  borderTop: '1px solid #e5ebf3',
                  padding: 16,
                  display: 'flex',
                  gap: 12,
                }}
              >
                <input
                  type="text"
                  value={inputMessage}
                  onChange={e => setInputMessage(e.target.value)}
                  placeholder={`Ask anything about ${activeSession.subject}…`}
                  disabled={streaming}
                  style={{
                    flex: 1,
                    padding: '12px 16px',
                    border: '1px solid #cbd5e1',
                    borderRadius: 10,
                    fontSize: 15,
                    outline: 'none',
                  }}
                />
                <button
                  type="submit"
                  disabled={streaming || !inputMessage.trim()}
                  className="prof-action-btn prof-action-btn-primary"
                  style={{
                    padding: '12px 28px',
                    fontSize: 15,
                    opacity: (streaming || !inputMessage.trim()) ? 0.5 : 1,
                  }}
                >
                  {streaming ? 'Thinking…' : 'Send'}
                </button>
              </form>
            </>
          ) : (
            <div style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexDirection: 'column',
              padding: 40,
            }}>
              <div style={{ fontSize: '4rem', marginBottom: 16 }}>🎓</div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f3460', marginBottom: 8 }}>
                Start a New Tutor Session
              </h2>
              <p style={{ color: '#64748b', marginBottom: 24 }}>
                Choose a subject and language to begin learning
              </p>
              <button
                onClick={() => setShowNewModal(true)}
                className="prof-action-btn prof-action-btn-primary"
                style={{ padding: '12px 32px', fontSize: 16 }}
              >
                + Create Session
              </button>
            </div>
          )}
        </main>
      </div>

      {showNewModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(15, 52, 96, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 50,
            padding: 16,
          }}
          onClick={() => setShowNewModal(false)}
        >
          <div
            style={{
              background: '#fff',
              borderRadius: 14,
              padding: 28,
              maxWidth: 480,
              width: '100%',
              boxShadow: '0 20px 50px rgba(15, 52, 96, 0.25)',
            }}
            onClick={e => e.stopPropagation()}
          >
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f3460', marginBottom: 20 }}>
              New Tutor Session
            </h2>
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: 14, fontWeight: 600, color: '#334155', marginBottom: 6 }}>
                Subject
              </label>
              <select
                value={subject}
                onChange={e => setSubject(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', border: '1px solid #cbd5e1', borderRadius: 8, fontSize: 14 }}
              >
                {subjects.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div style={{ marginBottom: 24 }}>
              <label style={{ display: 'block', fontSize: 14, fontWeight: 600, color: '#334155', marginBottom: 6 }}>
                Language
              </label>
              <select
                value={language}
                onChange={e => setLanguage(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', border: '1px solid #cbd5e1', borderRadius: 8, fontSize: 14 }}
              >
                <option value="en">English</option>
                <option value="kn">Kannada (ಕನ್ನಡ)</option>
              </select>
            </div>
            <div style={{ display: 'flex', gap: 12 }}>
              <button
                onClick={createSession}
                className="prof-action-btn prof-action-btn-primary"
                style={{ flex: 1, padding: '10px' }}
              >
                Create Session
              </button>
              <button
                onClick={() => setShowNewModal(false)}
                style={{
                  padding: '10px 20px',
                  background: '#f1f5f9',
                  color: '#475569',
                  border: 'none',
                  borderRadius: 8,
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
