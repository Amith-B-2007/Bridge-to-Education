import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';

export const DoubtChat = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [newDoubt, setNewDoubt] = useState({ subject: 'Maths', description: '' });
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);

  const subjects = ['Kannada', 'English', 'Maths', 'Science', 'Social Science'];

  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (activeSession) {
      fetchMessages(activeSession.id);
      connectWebSocket(activeSession.id);
    }
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [activeSession?.id]);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const response = await api.get('/doubts/sessions/');
      const data = response.data.results || response.data || [];
      setSessions(data);
      if (data.length > 0 && !activeSession) {
        setActiveSession(data[0]);
      }
    } catch (error) {
      console.error('Error fetching sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (sessionId) => {
    try {
      const response = await api.get(`/doubts/sessions/${sessionId}/`);
      setMessages(response.data.messages || []);
    } catch (error) {
      console.error('Error fetching messages:', error);
      setMessages([]);
    }
  };

  const connectWebSocket = (sessionId) => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    const token = localStorage.getItem('access_token');
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    try {
      wsRef.current = new WebSocket(`${wsHost}/ws/doubts/${sessionId}/?token=${token}`);
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'message') {
          setMessages(prev => [...prev, {
            id: data.message_id,
            sender_name: data.sender,
            message: data.text,
            created_at: data.timestamp,
          }]);
        }
      };
      wsRef.current.onerror = (e) => console.error('WS Error:', e);
    } catch (e) {
      console.error('WebSocket connection failed:', e);
    }
  };

  const createSession = async () => {
    if (!newDoubt.description.trim()) return;
    try {
      const response = await api.post('/doubts/sessions/', newDoubt);
      const newSession = response.data;
      setSessions([newSession, ...sessions]);
      setActiveSession(newSession);
      setShowCreateModal(false);
      setNewDoubt({ subject: 'Maths', description: '' });
    } catch (error) {
      console.error('Error creating session:', error);
      alert('Failed to create doubt session');
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || !activeSession) return;

    const messageText = inputMessage;
    setInputMessage('');

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ message: messageText }));
    } else {
      try {
        const response = await api.post(`/doubts/sessions/${activeSession.id}/messages/`, {
          message: messageText,
        });
        setMessages(prev => [...prev, response.data]);
      } catch (error) {
        console.error('Error sending message:', error);
        setInputMessage(messageText);
      }
    }
  };

  return (
    <div className="flex h-screen bg-slate-100">
      <div className="w-72 bg-white shadow-lg flex flex-col">
        <div className="p-4 border-b border-slate-200 bg-slate-50">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-cyan-700 hover:text-cyan-800 text-sm mb-3 font-semibold"
          >
            ← Back
          </button>
          <h2 className="text-lg font-bold text-slate-900 mb-3">💬 My Doubts</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="w-full bg-cyan-600 text-white py-2 rounded-lg text-sm hover:bg-cyan-700"
          >
            + New Doubt
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="p-4 text-gray-500 text-sm">Loading...</div>
          ) : sessions.length === 0 ? (
            <div className="p-4 text-gray-500 text-sm">
              No doubts yet. Click "New Doubt" to ask a question!
            </div>
          ) : (
            sessions.map(s => (
              <button
                key={s.id}
                onClick={() => setActiveSession(s)}
                className={`w-full text-left p-3 border-b border-slate-100 hover:bg-slate-50 ${
                  activeSession?.id === s.id ? 'bg-cyan-50 border-l-4 border-l-cyan-600' : ''
                }`}
              >
                <div className="font-medium text-gray-900 text-sm">{s.subject}</div>
                <div className="text-xs text-gray-500 mt-1 line-clamp-2">
                  {s.description}
                </div>
                <div className="flex justify-between items-center mt-2">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    s.status === 'resolved' ? 'bg-green-100 text-green-800' :
                    s.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {s.status}
                  </span>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        {activeSession ? (
          <>
            <div className="bg-white border-b border-slate-200 p-4">
              <h1 className="text-xl font-bold text-slate-900">{activeSession.subject}</h1>
              <p className="text-sm text-slate-600">{activeSession.description}</p>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50">
              {messages.length === 0 ? (
                <div className="text-center text-gray-500 py-12">
                  <p className="text-lg">No messages yet</p>
                  <p className="text-sm mt-2">Start the conversation by asking your doubt</p>
                </div>
              ) : (
                messages.map((msg, i) => {
                  const isMe = msg.sender_name === user?.username;
                  return (
                    <div key={msg.id || i} className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-md rounded-lg p-3 ${
                        isMe ? 'bg-cyan-600 text-white' : 'bg-white shadow border border-slate-200'
                      }`}>
                        <div className="text-xs opacity-75 mb-1">{msg.sender_name}</div>
                        <div>{msg.message}</div>
                      </div>
                    </div>
                  );
                })
              )}
              <div ref={messagesEndRef} />
            </div>

            <form onSubmit={sendMessage} className="bg-white border-t border-slate-200 p-4 flex gap-3">
              <input
                type="text"
                value={inputMessage}
                onChange={e => setInputMessage(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100"
              />
              <button
                type="submit"
                disabled={!inputMessage.trim()}
                className="bg-cyan-600 text-white px-6 py-2 rounded-lg hover:bg-cyan-700 disabled:opacity-50"
              >
                Send
              </button>
            </form>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center bg-gray-50">
            <div className="text-center">
              <p className="text-gray-500 text-lg mb-4">Select a doubt to chat or create a new one</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-cyan-600 text-white px-6 py-2 rounded-lg hover:bg-cyan-700"
              >
                + Create New Doubt
              </button>
            </div>
          </div>
        )}
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl border border-slate-200 max-w-lg w-full p-6">
            <h2 className="text-2xl font-bold mb-4">Ask a New Doubt</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                <select
                  value={newDoubt.subject}
                  onChange={e => setNewDoubt({...newDoubt, subject: e.target.value})}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-100 focus:border-cyan-500"
                >
                  {subjects.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Your Question</label>
                <textarea
                  value={newDoubt.description}
                  onChange={e => setNewDoubt({...newDoubt, description: e.target.value})}
                  rows="4"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-100 focus:border-cyan-500"
                  placeholder="Describe your doubt in detail..."
                />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={createSession}
                disabled={!newDoubt.description.trim()}
                className="flex-1 bg-cyan-600 text-white py-2 rounded-lg hover:bg-cyan-700 disabled:opacity-50"
              >
                Submit Doubt
              </button>
              <button
                onClick={() => setShowCreateModal(false)}
                className="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-300"
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
