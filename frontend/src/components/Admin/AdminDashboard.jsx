import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';

export const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState({ users: 0, students: 0, teachers: 0, quizzes: 0, resources: 0, doubts: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchStats(); }, []);

  const fetchStats = async () => {
    try {
      const [studentsRes, doubtsRes, resourcesRes, quizzesRes] = await Promise.allSettled([
        api.get('/users/students/'),
        api.get('/doubts/sessions/'),
        api.get('/resources/resources/'),
        api.get('/quizzes/'),
      ]);
      setStats({
        students: studentsRes.value?.data?.count ?? studentsRes.value?.data?.length ?? 0,
        doubts: doubtsRes.value?.data?.count ?? doubtsRes.value?.data?.length ?? 0,
        resources: resourcesRes.value?.data?.count ?? resourcesRes.value?.data?.length ?? 0,
        quizzes: quizzesRes.value?.data?.count ?? quizzesRes.value?.data?.length ?? 0,
        users: 0,
        teachers: 0,
      });
    } catch (e) {
      console.error('Stats error', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prof-page-shell">
      <header className="prof-page-header">
        <div className="prof-page-header-inner">
          <div>
            <h1 className="prof-page-title">⚙️ Admin Console</h1>
            <p className="prof-page-subtitle">Welcome, {user?.username} · Platform overview & management</p>
          </div>
          <button
            onClick={logout}
            className="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg border border-white/20"
          >
            Logout
          </button>
        </div>
      </header>

      <nav className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-1">
            {[
              { id: 'overview', label: '📊 Overview' },
              { id: 'users', label: '👥 Users' },
              { id: 'content', label: '📚 Content' },
              { id: 'system', label: '🔧 System' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 font-medium ${
                  activeTab === tab.id
                    ? 'border-b-2 border-cyan-600 text-cyan-700'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      <main className="prof-main">
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600"></div>
          </div>
        ) : activeTab === 'overview' ? (
          <Overview stats={stats} />
        ) : activeTab === 'users' ? (
          <UsersPanel />
        ) : activeTab === 'content' ? (
          <ContentPanel stats={stats} />
        ) : (
          <SystemPanel />
        )}
      </main>
    </div>
  );
};

const StatCard = ({ icon, label, value, accent }) => (
  <div className="prof-surface" style={{ padding: 24 }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <div style={{
        width: 48, height: 48, borderRadius: 12, background: accent,
        display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24,
      }}>
        {icon}
      </div>
      <div>
        <p style={{ color: '#64748b', fontSize: 13, fontWeight: 500 }}>{label}</p>
        <p style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0f3460' }}>{value}</p>
      </div>
    </div>
  </div>
);

const Overview = ({ stats }) => (
  <div>
    <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f3460', marginBottom: 20 }}>
      Platform Statistics
    </h2>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatCard icon="🎓" label="Students" value={stats.students} accent="#e0f6ff" />
      <StatCard icon="📝" label="Quizzes" value={stats.quizzes} accent="#dcfce7" />
      <StatCard icon="📚" label="Resources" value={stats.resources} accent="#fef3c7" />
      <StatCard icon="💬" label="Doubts" value={stats.doubts} accent="#fce7f3" />
    </div>

    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="prof-surface" style={{ padding: 28 }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#0f3460', marginBottom: 16 }}>
          🚀 Quick Actions
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <a
            href="/admin/" target="_blank" rel="noreferrer"
            className="prof-action-btn prof-action-btn-primary"
            style={{ padding: '12px 16px', textAlign: 'center', textDecoration: 'none' }}
          >
            Open Django Admin
          </a>
          <button
            className="prof-action-btn"
            style={{ padding: '12px 16px', background: '#f1f5f9', color: '#0f3460', border: '1px solid #cbd5e1' }}
          >
            View System Logs
          </button>
          <button
            className="prof-action-btn"
            style={{ padding: '12px 16px', background: '#f1f5f9', color: '#0f3460', border: '1px solid #cbd5e1' }}
          >
            Export User Data
          </button>
        </div>
      </div>

      <div className="prof-surface" style={{ padding: 28 }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#0f3460', marginBottom: 16 }}>
          📈 Recent Activity
        </h3>
        <ul style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
          {[
            { color: '#0084d1', text: 'New student registered', time: '2 min ago' },
            { color: '#10b981', text: 'Quiz uploaded by teacher', time: '15 min ago' },
            { color: '#f59e0b', text: '3 new doubt sessions opened', time: '1 hr ago' },
            { color: '#ef4444', text: 'SMS notifications sent: 12', time: '2 hr ago' },
          ].map((item, i) => (
            <li key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 0', borderBottom: '1px solid #f1f5f9' }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: item.color }} />
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14, color: '#334155' }}>{item.text}</div>
                <div style={{ fontSize: 12, color: '#94a3b8' }}>{item.time}</div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  </div>
);

const UsersPanel = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/users/students/')
      .then(r => setUsers(r.data.results || r.data || []))
      .catch(() => setUsers([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="prof-surface">
      <div style={{ padding: 24, borderBottom: '1px solid #e5ebf3' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f3460' }}>User Management</h2>
        <p style={{ color: '#64748b', fontSize: 14, marginTop: 4 }}>
          View and manage all students, teachers and mentors
        </p>
      </div>
      {loading ? (
        <div style={{ padding: 48, textAlign: 'center', color: '#64748b' }}>Loading…</div>
      ) : users.length === 0 ? (
        <div style={{ padding: 48, textAlign: 'center', color: '#64748b' }}>No users found</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f8fafc' }}>
                <th style={{ textAlign: 'left', padding: 12, fontSize: 12, color: '#64748b', textTransform: 'uppercase' }}>Username</th>
                <th style={{ textAlign: 'left', padding: 12, fontSize: 12, color: '#64748b', textTransform: 'uppercase' }}>Name</th>
                <th style={{ textAlign: 'left', padding: 12, fontSize: 12, color: '#64748b', textTransform: 'uppercase' }}>Grade</th>
                <th style={{ textAlign: 'left', padding: 12, fontSize: 12, color: '#64748b', textTransform: 'uppercase' }}>Quiz Attempts</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                  <td style={{ padding: 12, fontSize: 14, fontWeight: 600, color: '#0f3460' }}>{u.user?.username}</td>
                  <td style={{ padding: 12, fontSize: 14, color: '#334155' }}>
                    {u.user?.first_name} {u.user?.last_name}
                  </td>
                  <td style={{ padding: 12, fontSize: 14, color: '#334155' }}>Grade {u.grade}</td>
                  <td style={{ padding: 12, fontSize: 14, color: '#334155' }}>{u.total_quiz_attempts || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

const ContentPanel = ({ stats }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
    <div className="prof-surface" style={{ padding: 28 }}>
      <div style={{ fontSize: '2.5rem' }}>📚</div>
      <h3 style={{ fontWeight: 700, fontSize: '1.25rem', color: '#0f3460', margin: '12px 0 8px' }}>
        Resources
      </h3>
      <p style={{ color: '#64748b', marginBottom: 12 }}>
        {stats.resources} learning resources currently available across all grades
      </p>
      <a href="/resources" className="prof-action-btn prof-action-btn-primary" style={{ padding: '8px 16px', textDecoration: 'none', display: 'inline-block' }}>
        Manage Resources
      </a>
    </div>
    <div className="prof-surface" style={{ padding: 28 }}>
      <div style={{ fontSize: '2.5rem' }}>📝</div>
      <h3 style={{ fontWeight: 700, fontSize: '1.25rem', color: '#0f3460', margin: '12px 0 8px' }}>
        Quizzes
      </h3>
      <p style={{ color: '#64748b', marginBottom: 12 }}>
        {stats.quizzes} quizzes available for assessment
      </p>
      <a href="/quizzes" className="prof-action-btn prof-action-btn-primary" style={{ padding: '8px 16px', textDecoration: 'none', display: 'inline-block' }}>
        Manage Quizzes
      </a>
    </div>
  </div>
);

const SystemPanel = () => (
  <div className="prof-surface" style={{ padding: 28 }}>
    <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f3460', marginBottom: 16 }}>
      🔧 System Information
    </h3>
    <div style={{ display: 'grid', gap: 12 }}>
      {[
        ['API Endpoint', 'http://localhost:8000/api'],
        ['Database', 'SQLite (development)'],
        ['Authentication', 'JWT (1 hour access, 7 day refresh)'],
        ['Frontend', 'React 18 + Vite + Tailwind'],
        ['Backend', 'Django 4.2 + DRF'],
      ].map(([k, v], i) => (
        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #f1f5f9' }}>
          <span style={{ color: '#64748b', fontSize: 14 }}>{k}</span>
          <span style={{ color: '#0f3460', fontSize: 14, fontWeight: 600 }}>{v}</span>
        </div>
      ))}
    </div>
  </div>
);
