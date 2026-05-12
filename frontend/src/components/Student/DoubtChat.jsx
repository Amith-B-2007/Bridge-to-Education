import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';

const SUBJECTS = ['Kannada', 'Hindi', 'Marathi', 'English', 'Maths', 'Science', 'Social Science', 'Schemes & Scholarships'];

const STATUS_STYLE = {
  open:        { bg: '#fef9c3', color: '#854d0e', label: 'Open' },
  in_progress: { bg: '#dbeafe', color: '#1d4ed8', label: 'In Progress' },
  resolved:    { bg: '#dcfce7', color: '#166534', label: 'Resolved' },
};

export const DoubtChat = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [newDoubt, setNewDoubt] = useState({ subject: 'Maths', description: '' });
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => { fetchSessions(); }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (activeSession) {
      fetchMessages(activeSession.id);
      connectWebSocket(activeSession.id);
    }
    return () => { wsRef.current?.close(); };
  }, [activeSession?.id]);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const res = await api.get('/doubts/sessions/');
      const data = res.data.results || res.data || [];
      setSessions(data);
      if (data.length > 0 && !activeSession) setActiveSession(data[0]);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const fetchMessages = async (id) => {
    try {
      const res = await api.get(`/doubts/sessions/${id}/`);
      setMessages(res.data.messages || []);
    } catch (e) { setMessages([]); }
  };

  const connectWebSocket = (sessionId) => {
    wsRef.current?.close();
    const token = localStorage.getItem('access_token');
    const wsHost = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    try {
      wsRef.current = new WebSocket(`${wsHost}/ws/doubts/${sessionId}/?token=${token}`);
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'message') {
          setMessages(prev => [...prev, { id: data.message_id, sender_name: data.sender, message: data.text, created_at: data.timestamp }]);
        }
      };
    } catch (e) { console.error('WebSocket failed:', e); }
  };

  const createSession = async () => {
    if (!newDoubt.description.trim()) return;
    try {
      const res = await api.post('/doubts/sessions/', newDoubt);
      setSessions(prev => [res.data, ...prev]);
      setActiveSession(res.data);
      setShowCreateModal(false);
      setNewDoubt({ subject: 'Maths', description: '' });
    } catch (e) { alert('Failed to create doubt session'); }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || !activeSession) return;
    const text = inputMessage;
    setInputMessage('');
    setSending(true);
    try {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ message: text }));
      } else {
        const res = await api.post(`/doubts/sessions/${activeSession.id}/messages/`, { message: text });
        setMessages(prev => [...prev, res.data]);
      }
    } catch (e) { setInputMessage(text); }
    finally { setSending(false); }
  };

  const statusStyle = activeSession ? (STATUS_STYLE[activeSession.status] || STATUS_STYLE.open) : STATUS_STYLE.open;

  return (
    <div className="prof-page-shell" style={{ display: 'flex', flexDirection: 'column' }}>
      {/* Top header */}
      <header className="prof-page-header">
        <div className="prof-page-header-inner">
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <button
              onClick={() => navigate('/dashboard')}
              style={{ background: 'rgba(255,255,255,0.12)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff', borderRadius: 8, padding: '6px 14px', cursor: 'pointer', fontWeight: 600, fontSize: 14 }}
            >
              ← Back
            </button>
            <div>
              <h1 className="prof-page-title">💬 My Doubts</h1>
              <p className="prof-page-subtitle">Ask questions and get help from teachers</p>
            </div>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            style={{ background: 'linear-gradient(135deg, #00a8e8, #0084d1)', color: '#fff', border: 'none', borderRadius: 9, padding: '9px 18px', fontWeight: 700, fontSize: 14, cursor: 'pointer' }}
          >
            + New Doubt
          </button>
        </div>
      </header>

      {/* Main body: sidebar + chat */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden', height: 'calc(100vh - 76px)' }}>

        {/* Sidebar */}
        <div style={{ width: 300, minWidth: 300, background: '#fff', borderRight: '1px solid #e5ebf3', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ padding: '14px 16px', borderBottom: '1px solid #e5ebf3', background: '#f8fafc' }}>
            <p style={{ fontSize: 12, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              {sessions.length} Session{sessions.length !== 1 ? 's' : ''}
            </p>
          </div>

          <div style={{ flex: 1, overflowY: 'auto' }}>
            {loading ? (
              <div style={{ padding: 24, textAlign: 'center', color: '#94a3b8' }}>Loading…</div>
            ) : sessions.length === 0 ? (
              <div style={{ padding: 24, textAlign: 'center' }}>
                <div style={{ fontSize: '2.5rem', marginBottom: 8 }}>💬</div>
                <p style={{ color: '#94a3b8', fontSize: 13 }}>No doubts yet.<br />Click New Doubt to start!</p>
              </div>
            ) : sessions.map(s => {
              const ss = STATUS_STYLE[s.status] || STATUS_STYLE.open;
              const isActive = activeSession?.id === s.id;
              return (
                <button
                  key={s.id}
                  onClick={() => setActiveSession(s)}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    padding: '14px 16px',
                    borderBottom: '1px solid #f1f5f9',
                    background: isActive ? '#f0f9ff' : 'transparent',
                    borderLeft: isActive ? '3px solid #0084d1' : '3px solid transparent',
                    cursor: 'pointer',
                    border: 'none',
                    borderBottom: '1px solid #f1f5f9',
                    borderLeft: isActive ? '3px solid #0084d1' : '3px solid transparent',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                    <span style={{ fontWeight: 700, fontSize: 13, color: '#1e293b' }}>{s.subject}</span>
                    <span style={{ background: ss.bg, color: ss.color, fontSize: 10, fontWeight: 700, padding: '2px 7px', borderRadius: 10, textTransform: 'uppercase' }}>
                      {ss.label}
                    </span>
                  </div>
                  <p style={{ fontSize: 12, color: '#64748b', lineHeight: 1.4, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', margin: 0 }}>
                    {s.description}
                  </p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Chat area */}
        {activeSession ? (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            {/* Chat header */}
            <div style={{ padding: '14px 24px', borderBottom: '1px solid #e5ebf3', background: '#fff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2 style={{ fontWeight: 700, fontSize: 16, color: '#1e293b', margin: 0 }}>{activeSession.subject}</h2>
                <p style={{ fontSize: 12, color: '#64748b', marginTop: 2, maxWidth: 500 }}>{activeSession.description}</p>
              </div>
              <span style={{ background: statusStyle.bg, color: statusStyle.color, fontSize: 11, fontWeight: 700, padding: '4px 12px', borderRadius: 12, textTransform: 'uppercase', whiteSpace: 'nowrap' }}>
                {statusStyle.label}
              </span>
            </div>

            {/* Messages */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '24px', background: '#f8fafc', display: 'flex', flexDirection: 'column', gap: 12 }}>
              {messages.length === 0 ? (
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#94a3b8' }}>
                  <div style={{ fontSize: '2.5rem', marginBottom: 8 }}>💬</div>
                  <p style={{ fontSize: 14 }}>No messages yet — start the conversation!</p>
                </div>
              ) : messages.map((msg, i) => {
                const isMe = msg.sender_name === user?.username;
                return (
                  <div key={msg.id || i} style={{ display: 'flex', justifyContent: isMe ? 'flex-end' : 'flex-start' }}>
                    {!isMe && (
                      <div style={{ width: 32, height: 32, borderRadius: '50%', background: '#e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 700, color: '#64748b', flexShrink: 0, marginRight: 8, alignSelf: 'flex-end' }}>
                        {(msg.sender_name || 'T')[0].toUpperCase()}
                      </div>
                    )}
                    <div style={{ maxWidth: '65%' }}>
                      {!isMe && (
                        <div style={{ fontSize: 11, color: '#94a3b8', fontWeight: 600, marginBottom: 3, paddingLeft: 4 }}>{msg.sender_name}</div>
                      )}
                      <div style={{
                        padding: '10px 14px',
                        borderRadius: isMe ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                        background: isMe ? 'linear-gradient(135deg, #0084d1, #0066aa)' : '#fff',
                        color: isMe ? '#fff' : '#1e293b',
                        fontSize: 14,
                        lineHeight: 1.5,
                        boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
                        border: isMe ? 'none' : '1px solid #e5ebf3',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                      }}>
                        {msg.message}
                      </div>
                      <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 3, textAlign: isMe ? 'right' : 'left', paddingLeft: 4 }}>
                        {msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                      </div>
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={sendMessage} style={{ padding: '14px 24px', background: '#fff', borderTop: '1px solid #e5ebf3', display: 'flex', gap: 10 }}>
              <input
                type="text"
                value={inputMessage}
                onChange={e => setInputMessage(e.target.value)}
                placeholder="Type your message…"
                disabled={sending}
                style={{ flex: 1, padding: '10px 16px', border: '1.5px solid #e2e8f0', borderRadius: 10, fontSize: 14, outline: 'none', color: '#1e293b', background: '#f8fafc' }}
                onFocus={e => e.target.style.borderColor = '#0084d1'}
                onBlur={e => e.target.style.borderColor = '#e2e8f0'}
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || sending}
                style={{ background: inputMessage.trim() && !sending ? 'linear-gradient(135deg, #00a8e8, #0084d1)' : '#e2e8f0', color: inputMessage.trim() && !sending ? '#fff' : '#94a3b8', border: 'none', borderRadius: 10, padding: '10px 20px', fontWeight: 700, fontSize: 14, cursor: inputMessage.trim() && !sending ? 'pointer' : 'default', transition: 'all 0.15s' }}
              >
                {sending ? '…' : 'Send'}
              </button>
            </form>
          </div>
        ) : (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: '#f8fafc', gap: 16 }}>
            <div style={{ fontSize: '4rem' }}>💬</div>
            <p style={{ color: '#64748b', fontSize: 16, fontWeight: 500 }}>Select a doubt from the left to view the conversation</p>
            <button
              onClick={() => setShowCreateModal(true)}
              style={{ background: 'linear-gradient(135deg, #00a8e8, #0084d1)', color: '#fff', border: 'none', borderRadius: 9, padding: '10px 20px', fontWeight: 700, cursor: 'pointer' }}
            >
              + Ask New Doubt
            </button>
          </div>
        )}
      </div>

      {/* Create modal */}
      {showCreateModal && (
        <div
          onClick={() => setShowCreateModal(false)}
          style={{ position: 'fixed', inset: 0, background: 'rgba(15,52,96,0.45)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16, zIndex: 50 }}
        >
          <div
            onClick={e => e.stopPropagation()}
            style={{ background: '#fff', borderRadius: 16, width: '100%', maxWidth: 500, boxShadow: '0 20px 50px rgba(15,52,96,0.2)', overflow: 'hidden' }}
          >
            <div style={{ background: 'linear-gradient(135deg, #0f3460, #16213e)', padding: '20px 24px' }}>
              <h2 style={{ color: '#fff', fontWeight: 800, fontSize: '1.2rem', margin: 0 }}>Ask a New Doubt</h2>
              <p style={{ color: '#d8e2ef', fontSize: 13, marginTop: 4 }}>Your teacher will respond as soon as possible</p>
            </div>
            <div style={{ padding: 24 }}>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>Subject</label>
                <select
                  value={newDoubt.subject}
                  onChange={e => setNewDoubt({ ...newDoubt, subject: e.target.value })}
                  style={{ width: '100%', padding: '10px 14px', border: '1.5px solid #e2e8f0', borderRadius: 9, fontSize: 14, color: '#1e293b', background: '#fff' }}
                >
                  {SUBJECTS.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div style={{ marginBottom: 24 }}>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>Your Question</label>
                <textarea
                  value={newDoubt.description}
                  onChange={e => setNewDoubt({ ...newDoubt, description: e.target.value })}
                  rows={4}
                  placeholder="Describe your doubt clearly…"
                  style={{ width: '100%', padding: '10px 14px', border: '1.5px solid #e2e8f0', borderRadius: 9, fontSize: 14, color: '#1e293b', resize: 'vertical', outline: 'none', boxSizing: 'border-box' }}
                />
              </div>
              <div style={{ display: 'flex', gap: 10 }}>
                <button
                  onClick={createSession}
                  disabled={!newDoubt.description.trim()}
                  style={{ flex: 1, background: newDoubt.description.trim() ? 'linear-gradient(135deg, #00a8e8, #0084d1)' : '#e2e8f0', color: newDoubt.description.trim() ? '#fff' : '#94a3b8', border: 'none', borderRadius: 9, padding: '11px 0', fontWeight: 700, fontSize: 14, cursor: newDoubt.description.trim() ? 'pointer' : 'default' }}
                >
                  Submit Doubt
                </button>
                <button
                  onClick={() => setShowCreateModal(false)}
                  style={{ padding: '11px 20px', border: '1.5px solid #e2e8f0', borderRadius: 9, background: '#fff', color: '#64748b', cursor: 'pointer', fontWeight: 600, fontSize: 14 }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
