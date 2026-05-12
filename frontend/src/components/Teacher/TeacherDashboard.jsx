import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';

const SUBJECT_LABELS = {
  maths: 'Mathematics', science: 'Science', english: 'English',
  kannada: 'Kannada', social_science: 'Social Science',
  hindi: 'Hindi', marathi: 'Marathi',
};

const SCORE_STYLE = (pct) => {
  if (pct >= 80) return { bg: '#dcfce7', color: '#166534', label: `${pct}%` };
  if (pct >= 60) return { bg: '#fef9c3', color: '#854d0e', label: `${pct}%` };
  if (pct >= 40) return { bg: '#ffedd5', color: '#9a3412', label: `${pct}%` };
  return { bg: '#fee2e2', color: '#991b1b', label: `${pct}%` };
};

const ATT_STYLE = (pct) => {
  if (pct >= 85) return { color: '#166534' };
  if (pct >= 75) return { color: '#854d0e' };
  return { color: '#991b1b' };
};

export const TeacherDashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [doubts, setDoubts] = useState([]);
  const [students, setStudents] = useState([]);
  const [loadingDoubts, setLoadingDoubts] = useState(true);
  const [loadingStudents, setLoadingStudents] = useState(true);

  useEffect(() => {
    fetchDoubts();
    fetchStudents();
  }, []);

  const fetchDoubts = async () => {
    setLoadingDoubts(true);
    try {
      const res = await api.get('/doubts/sessions/?status=open');
      setDoubts(res.data.results || res.data || []);
    } catch (e) { console.error(e); }
    finally { setLoadingDoubts(false); }
  };

  const fetchStudents = async () => {
    setLoadingStudents(true);
    try {
      const res = await api.get('/users/students/');
      setStudents(res.data.students || []);
    } catch (e) { console.error(e); }
    finally { setLoadingStudents(false); }
  };

  const avgScore = students.length
    ? Math.round(students.reduce((s, st) => s + st.avg_score, 0) / students.length)
    : 0;
  const avgAttendance = students.length
    ? Math.round(students.reduce((s, st) => s + st.attendance, 0) / students.length)
    : 0;

  const TABS = [
    { id: 'overview',  label: 'Overview',  icon: '📊' },
    { id: 'students',  label: 'Students',  icon: '👥' },
    { id: 'doubts',    label: 'Doubts',    icon: '💬', badge: doubts.length },
    { id: 'upload',    label: 'Resources', icon: '📤' },
    { id: 'marks',     label: 'Marks',     icon: '📝' },
  ];

  return (
    <div style={{ minHeight: '100vh', background: '#f3f6fb', fontFamily: 'inherit' }}>
      {/* Header */}
      <header style={{ background: 'linear-gradient(135deg, #0f3460 0%, #16213e 100%)', color: '#fff' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '20px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: '1.6rem', fontWeight: 800, margin: 0 }}>👨‍🏫 Teacher Portal</h1>
            <p style={{ color: '#d8e2ef', fontSize: 13, marginTop: 4 }}>Welcome back, {user?.first_name || user?.username}</p>
          </div>
          <button
            onClick={logout}
            style={{ background: 'rgba(255,255,255,0.12)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff', borderRadius: 8, padding: '8px 18px', cursor: 'pointer', fontWeight: 600, fontSize: 14 }}
          >
            Logout
          </button>
        </div>

        {/* Tabs inside header bottom */}
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px', display: 'flex', gap: 4 }}>
          {TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '10px 18px',
                border: 'none',
                background: activeTab === tab.id ? 'rgba(255,255,255,0.15)' : 'transparent',
                color: activeTab === tab.id ? '#fff' : 'rgba(255,255,255,0.6)',
                borderRadius: '8px 8px 0 0',
                fontWeight: activeTab === tab.id ? 700 : 500,
                fontSize: 14,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                borderBottom: activeTab === tab.id ? '2px solid #00a8e8' : '2px solid transparent',
                transition: 'all 0.15s',
              }}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
              {tab.badge > 0 && (
                <span style={{ background: '#ef4444', color: '#fff', borderRadius: 10, padding: '1px 6px', fontSize: 11, fontWeight: 800 }}>
                  {tab.badge}
                </span>
              )}
            </button>
          ))}
        </div>
      </header>

      {/* Content */}
      <main style={{ maxWidth: 1200, margin: '0 auto', padding: '32px 24px' }}>
        {activeTab === 'overview' && (
          <OverviewTab
            students={students}
            doubts={doubts}
            avgScore={avgScore}
            avgAttendance={avgAttendance}
            loadingStudents={loadingStudents}
            onNavigate={setActiveTab}
          />
        )}
        {activeTab === 'students' && (
          <StudentsTab students={students} loading={loadingStudents} />
        )}
        {activeTab === 'doubts' && (
          <DoubtsPanel doubts={doubts} loading={loadingDoubts} onRefresh={fetchDoubts} />
        )}
        {activeTab === 'upload' && <ResourceUpload />}
        {activeTab === 'marks' && <MarksUpload />}
      </main>
    </div>
  );
};

/* ── Overview ─────────────────────────────────────────────────────────────── */

const OverviewTab = ({ students, doubts, avgScore, avgAttendance, loadingStudents, onNavigate }) => {
  const sortedByScore = [...students].sort((a, b) => b.avg_score - a.avg_score);
  const topStudents = sortedByScore.slice(0, 3);
  const struggling = sortedByScore.filter(s => s.avg_score < 50).slice(0, 3);

  const stats = [
    { label: 'Total Students', value: students.length, icon: '👥', color: '#2563eb', bg: '#eff6ff' },
    { label: 'Open Doubts',    value: doubts.length,   icon: '💬', color: '#d97706', bg: '#fffbeb' },
    { label: 'Avg Quiz Score', value: `${avgScore}%`,  icon: '📊', color: '#059669', bg: '#f0fdf4' },
    { label: 'Avg Attendance', value: `${avgAttendance}%`, icon: '📅', color: '#7c3aed', bg: '#f5f3ff' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
        {stats.map(s => (
          <div key={s.label} style={{ background: '#fff', borderRadius: 14, border: '1px solid #e5ebf3', boxShadow: '0 2px 8px rgba(13,38,76,0.05)', padding: '22px 24px', display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{ width: 48, height: 48, borderRadius: 12, background: s.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', flexShrink: 0 }}>
              {s.icon}
            </div>
            <div>
              <div style={{ fontSize: '1.7rem', fontWeight: 800, color: s.color, lineHeight: 1 }}>{loadingStudents ? '…' : s.value}</div>
              <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>{s.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick actions */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
        {[
          { label: 'View All Students', icon: '👥', tab: 'students', color: '#2563eb' },
          { label: 'Answer Doubts', icon: '💬', tab: 'doubts', color: '#d97706' },
          { label: 'Upload Resources', icon: '📤', tab: 'upload', color: '#059669' },
          { label: 'Enter Marks', icon: '📝', tab: 'marks', color: '#7c3aed' },
        ].map(a => (
          <button
            key={a.tab}
            onClick={() => onNavigate(a.tab)}
            style={{ background: '#fff', border: `1.5px solid ${a.color}22`, borderRadius: 10, padding: '14px 16px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10, fontWeight: 600, color: a.color, fontSize: 14, textAlign: 'left', transition: 'background 0.15s' }}
            onMouseEnter={e => e.currentTarget.style.background = `${a.color}0a`}
            onMouseLeave={e => e.currentTarget.style.background = '#fff'}
          >
            <span style={{ fontSize: '1.3rem' }}>{a.icon}</span>{a.label}
          </button>
        ))}
      </div>

      {/* Student performance panels */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        {/* Top performers */}
        <div style={{ background: '#fff', borderRadius: 14, border: '1px solid #e5ebf3', boxShadow: '0 2px 8px rgba(13,38,76,0.05)', padding: '20px 24px' }}>
          <h3 style={{ fontWeight: 700, color: '#1e293b', marginBottom: 16, fontSize: 15, display: 'flex', alignItems: 'center', gap: 8 }}>
            🏆 Top Performers
          </h3>
          {topStudents.length === 0 ? (
            <p style={{ color: '#94a3b8', fontSize: 13 }}>No data yet</p>
          ) : topStudents.map((s, i) => {
            const sc = SCORE_STYLE(s.avg_score);
            return (
              <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 0', borderBottom: i < topStudents.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                <span style={{ width: 24, height: 24, borderRadius: '50%', background: ['#fbbf24', '#94a3b8', '#cd7c2f'][i] || '#e2e8f0', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 800, flexShrink: 0 }}>
                  {i + 1}
                </span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 14, color: '#1e293b' }}>{s.name}</div>
                  <div style={{ fontSize: 12, color: '#94a3b8' }}>Grade {s.grade}</div>
                </div>
                <span style={{ background: sc.bg, color: sc.color, padding: '3px 10px', borderRadius: 12, fontSize: 12, fontWeight: 700 }}>{sc.label}</span>
              </div>
            );
          })}
        </div>

        {/* Needs attention */}
        <div style={{ background: '#fff', borderRadius: 14, border: '1px solid #e5ebf3', boxShadow: '0 2px 8px rgba(13,38,76,0.05)', padding: '20px 24px' }}>
          <h3 style={{ fontWeight: 700, color: '#1e293b', marginBottom: 16, fontSize: 15, display: 'flex', alignItems: 'center', gap: 8 }}>
            ⚠️ Needs Attention
          </h3>
          {struggling.length === 0 ? (
            <p style={{ color: '#94a3b8', fontSize: 13 }}>All students doing well!</p>
          ) : struggling.map((s, i) => {
            const sc = SCORE_STYLE(s.avg_score);
            return (
              <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 0', borderBottom: i < struggling.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                <div style={{ width: 36, height: 36, borderRadius: '50%', background: '#fee2e2', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 800, color: '#991b1b', flexShrink: 0 }}>
                  {s.name[0]}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 14, color: '#1e293b' }}>{s.name}</div>
                  <div style={{ fontSize: 12, color: '#94a3b8' }}>Grade {s.grade} · {s.school}</div>
                </div>
                <span style={{ background: sc.bg, color: sc.color, padding: '3px 10px', borderRadius: 12, fontSize: 12, fontWeight: 700 }}>{sc.label}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

/* ── Students Tab ─────────────────────────────────────────────────────────── */

const StudentsTab = ({ students, loading }) => {
  const [gradeFilter, setGradeFilter] = useState('all');
  const [search, setSearch] = useState('');

  const filtered = students.filter(s => {
    const matchGrade = gradeFilter === 'all' || String(s.grade) === gradeFilter;
    const matchSearch = s.name.toLowerCase().includes(search.toLowerCase()) || s.school.toLowerCase().includes(search.toLowerCase());
    return matchGrade && matchSearch;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Controls */}
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
        <input
          placeholder="Search by name or school…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ padding: '9px 14px', border: '1.5px solid #e2e8f0', borderRadius: 9, fontSize: 14, color: '#1e293b', minWidth: 220, outline: 'none' }}
        />
        <select
          value={gradeFilter}
          onChange={e => setGradeFilter(e.target.value)}
          style={{ padding: '9px 14px', border: '1.5px solid #e2e8f0', borderRadius: 9, fontSize: 14, color: '#1e293b', background: '#fff', cursor: 'pointer' }}
        >
          <option value="all">All Grades</option>
          {[1,2,3,4,5,6,7,8,9,10].map(g => <option key={g} value={String(g)}>Grade {g}</option>)}
        </select>
        <span style={{ color: '#64748b', fontSize: 13 }}>{filtered.length} student{filtered.length !== 1 ? 's' : ''}</span>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 60, color: '#94a3b8' }}>Loading students…</div>
      ) : (
        <div style={{ background: '#fff', borderRadius: 14, border: '1px solid #e5ebf3', boxShadow: '0 2px 8px rgba(13,38,76,0.05)', overflow: 'hidden' }}>
          {/* Table header */}
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 2fr 1fr 1fr 1fr', padding: '12px 20px', background: '#f8fafc', borderBottom: '1px solid #e5ebf3' }}>
            {['Student', 'Grade', 'School', 'Avg Score', 'Attendance', 'Quizzes'].map(h => (
              <div key={h} style={{ fontSize: 11, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</div>
            ))}
          </div>

          {filtered.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>No students found</div>
          ) : filtered.map((s, i) => {
            const sc = SCORE_STYLE(s.avg_score);
            const att = ATT_STYLE(s.attendance);
            return (
              <div
                key={s.id}
                style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 2fr 1fr 1fr 1fr', padding: '14px 20px', borderBottom: i < filtered.length - 1 ? '1px solid #f1f5f9' : 'none', alignItems: 'center' }}
              >
                {/* Name + initials */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'linear-gradient(135deg, #0084d1, #005fa3)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 800, fontSize: 14, flexShrink: 0 }}>
                    {s.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 14, color: '#1e293b' }}>{s.name}</div>
                    <div style={{ fontSize: 11, color: '#94a3b8' }}>@{s.username}</div>
                  </div>
                </div>
                <div>
                  <span style={{ background: '#f1f5f9', color: '#475569', padding: '3px 10px', borderRadius: 10, fontSize: 12, fontWeight: 700 }}>Gr. {s.grade}</span>
                </div>
                <div style={{ fontSize: 13, color: '#475569', paddingRight: 8 }}>{s.school || '—'}</div>
                <div>
                  <span style={{ background: sc.bg, color: sc.color, padding: '4px 10px', borderRadius: 10, fontSize: 12, fontWeight: 700 }}>
                    {s.avg_score > 0 ? `${s.avg_score}%` : 'N/A'}
                  </span>
                </div>
                <div style={{ fontWeight: 700, fontSize: 14, color: att.color }}>{s.attendance}%</div>
                <div style={{ fontSize: 13, color: '#64748b' }}>{s.total_quiz_attempts} taken</div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

/* ── Doubts Panel ─────────────────────────────────────────────────────────── */

const DoubtsPanel = ({ doubts, loading, onRefresh }) => {
  const [activeDoubt, setActiveDoubt] = useState(null);

  const STATUS_STYLE = {
    open:        { bg: '#fef9c3', color: '#854d0e' },
    in_progress: { bg: '#dbeafe', color: '#1d4ed8' },
    resolved:    { bg: '#dcfce7', color: '#166534' },
  };

  const markResolved = async (id) => {
    if (!window.confirm('Mark as resolved?')) return;
    try {
      await api.post(`/doubts/sessions/${id}/resolve/`);
      onRefresh();
    } catch (e) { alert('Failed: ' + (e.response?.data?.detail || e.message)); }
  };

  return (
    <>
      <div style={{ background: '#fff', borderRadius: 14, border: '1px solid #e5ebf3', boxShadow: '0 2px 8px rgba(13,38,76,0.05)', overflow: 'hidden' }}>
        <div style={{ padding: '18px 24px', borderBottom: '1px solid #e5ebf3', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#f8fafc' }}>
          <h2 style={{ fontWeight: 700, fontSize: 16, color: '#1e293b', margin: 0 }}>Student Doubts</h2>
          <button onClick={onRefresh} style={{ background: 'transparent', border: '1.5px solid #e2e8f0', borderRadius: 7, padding: '6px 14px', cursor: 'pointer', fontWeight: 600, color: '#475569', fontSize: 13 }}>
            🔄 Refresh
          </button>
        </div>

        {loading ? (
          <div style={{ padding: 60, textAlign: 'center', color: '#94a3b8' }}>Loading doubts…</div>
        ) : doubts.length === 0 ? (
          <div style={{ padding: '60px 20px', textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', marginBottom: 12 }}>✅</div>
            <p style={{ color: '#64748b', fontSize: 15 }}>No open doubts at the moment.</p>
          </div>
        ) : doubts.map((doubt, i) => {
          const ss = STATUS_STYLE[doubt.status] || STATUS_STYLE.open;
          return (
            <div key={doubt.id} style={{ padding: '18px 24px', borderBottom: i < doubts.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                    <span style={{ fontWeight: 700, fontSize: 15, color: '#1e293b' }}>{doubt.subject}</span>
                    <span style={{ background: ss.bg, color: ss.color, fontSize: 10, fontWeight: 700, padding: '2px 8px', borderRadius: 10, textTransform: 'uppercase' }}>{doubt.status}</span>
                  </div>
                  <p style={{ fontSize: 12, color: '#64748b', marginBottom: 6 }}>From: <strong>{doubt.student_name}</strong></p>
                  <p style={{ fontSize: 14, color: '#334155', lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {doubt.description}
                  </p>
                </div>
              </div>
              <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                <button
                  onClick={() => setActiveDoubt(doubt)}
                  style={{ background: 'linear-gradient(135deg, #00a8e8, #0084d1)', color: '#fff', border: 'none', borderRadius: 7, padding: '7px 16px', cursor: 'pointer', fontWeight: 600, fontSize: 13 }}
                >
                  💬 Reply
                </button>
                {doubt.status !== 'resolved' && (
                  <button
                    onClick={() => markResolved(doubt.id)}
                    style={{ background: '#f0fdf4', color: '#166534', border: '1.5px solid #bbf7d0', borderRadius: 7, padding: '7px 16px', cursor: 'pointer', fontWeight: 600, fontSize: 13 }}
                  >
                    ✓ Resolve
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {activeDoubt && (
        <DoubtReplyModal
          doubt={activeDoubt}
          onClose={() => setActiveDoubt(null)}
          onSent={onRefresh}
        />
      )}
    </>
  );
};

/* ── Reply Modal ──────────────────────────────────────────────────────────── */

const DoubtReplyModal = ({ doubt, onClose, onSent }) => {
  const [messages, setMessages] = useState([]);
  const [reply, setReply] = useState('');
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => { loadMessages(); }, []);

  const loadMessages = async () => {
    try {
      const res = await api.get(`/doubts/sessions/${doubt.id}/`);
      setMessages(res.data.messages || []);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const sendReply = async (e) => {
    e.preventDefault();
    if (!reply.trim()) return;
    setSending(true);
    try {
      await api.post(`/doubts/sessions/${doubt.id}/messages/`, { message: reply });
      setReply('');
      await loadMessages();
      onSent?.();
    } catch (e) { alert('Failed: ' + (e.response?.data?.detail || e.message)); }
    finally { setSending(false); }
  };

  return (
    <div
      onClick={onClose}
      style={{ position: 'fixed', inset: 0, background: 'rgba(15,52,96,0.45)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16, zIndex: 50 }}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{ background: '#fff', borderRadius: 16, width: '100%', maxWidth: 600, maxHeight: '82vh', display: 'flex', flexDirection: 'column', boxShadow: '0 24px 60px rgba(15,52,96,0.2)', overflow: 'hidden' }}
      >
        {/* Modal header */}
        <div style={{ background: 'linear-gradient(135deg, #0f3460, #16213e)', padding: '18px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h2 style={{ color: '#fff', fontWeight: 800, fontSize: '1.1rem', margin: 0 }}>{doubt.subject}</h2>
            <p style={{ color: '#d8e2ef', fontSize: 12, marginTop: 4 }}>From: {doubt.student_name}</p>
            <p style={{ color: '#a5b4c8', fontSize: 13, marginTop: 6, lineHeight: 1.4 }}>{doubt.description}</p>
          </div>
          <button onClick={onClose} style={{ background: 'rgba(255,255,255,0.1)', border: 'none', color: '#fff', borderRadius: 6, width: 28, height: 28, cursor: 'pointer', fontSize: 16, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>×</button>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px', background: '#f8fafc', display: 'flex', flexDirection: 'column', gap: 10 }}>
          {loading ? (
            <p style={{ color: '#94a3b8', textAlign: 'center', padding: 20 }}>Loading…</p>
          ) : messages.length === 0 ? (
            <p style={{ color: '#94a3b8', textAlign: 'center', padding: 24 }}>No replies yet — be the first to help!</p>
          ) : messages.map((m, i) => {
            const isTeacher = m.sender_name === user?.username;
            return (
              <div key={m.id || i} style={{ display: 'flex', justifyContent: isTeacher ? 'flex-end' : 'flex-start' }}>
                <div style={{ maxWidth: '80%' }}>
                  <div style={{ fontSize: 11, color: '#94a3b8', fontWeight: 600, marginBottom: 3, textAlign: isTeacher ? 'right' : 'left', paddingLeft: 4 }}>{m.sender_name}</div>
                  <div style={{ padding: '10px 14px', borderRadius: isTeacher ? '14px 14px 4px 14px' : '14px 14px 14px 4px', background: isTeacher ? 'linear-gradient(135deg, #0084d1, #005fa3)' : '#fff', color: isTeacher ? '#fff' : '#1e293b', fontSize: 13, lineHeight: 1.5, boxShadow: '0 1px 4px rgba(0,0,0,0.07)', border: isTeacher ? 'none' : '1px solid #e5ebf3', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                    {m.message}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Input */}
        <form onSubmit={sendReply} style={{ padding: '14px 20px', borderTop: '1px solid #e5ebf3', display: 'flex', gap: 8 }}>
          <input
            type="text"
            value={reply}
            onChange={e => setReply(e.target.value)}
            placeholder="Type your reply…"
            disabled={sending}
            style={{ flex: 1, padding: '10px 14px', border: '1.5px solid #e2e8f0', borderRadius: 9, fontSize: 14, outline: 'none', color: '#1e293b' }}
          />
          <button
            type="submit"
            disabled={sending || !reply.trim()}
            style={{ background: reply.trim() && !sending ? 'linear-gradient(135deg, #00a8e8, #0084d1)' : '#e2e8f0', color: reply.trim() && !sending ? '#fff' : '#94a3b8', border: 'none', borderRadius: 9, padding: '10px 18px', cursor: reply.trim() && !sending ? 'pointer' : 'default', fontWeight: 700, fontSize: 14 }}
          >
            {sending ? '…' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
};

/* ── Resource Upload ──────────────────────────────────────────────────────── */

const ResourceUpload = () => {
  const [form, setForm] = useState({ title: '', description: '', grade: 5, subject: 'maths', chapter: '', resource_type: 'pdf' });
  const [file, setFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage('');
    try {
      const data = new FormData();
      Object.entries(form).forEach(([k, v]) => data.append(k, v));
      if (file) data.append('file', file);
      await api.post('/resources/resources/', data, { headers: { 'Content-Type': 'multipart/form-data' } });
      setMessage('success');
      setForm({ title: '', description: '', grade: 5, subject: 'maths', chapter: '', resource_type: 'pdf' });
      setFile(null);
    } catch (e) {
      setMessage('error:' + (e.response?.data?.detail || e.message));
    } finally { setSubmitting(false); }
  };

  const inputStyle = { width: '100%', padding: '10px 14px', border: '1.5px solid #e2e8f0', borderRadius: 9, fontSize: 14, color: '#1e293b', outline: 'none', boxSizing: 'border-box' };
  const labelStyle = { display: 'block', fontSize: 12, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 };

  return (
    <div style={{ background: '#fff', borderRadius: 14, border: '1px solid #e5ebf3', boxShadow: '0 2px 8px rgba(13,38,76,0.05)', maxWidth: 700, padding: '28px 32px' }}>
      <h2 style={{ fontWeight: 800, color: '#0f3460', fontSize: '1.2rem', marginBottom: 24 }}>📤 Upload Learning Resource</h2>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
          <label style={labelStyle}>Title</label>
          <input required style={inputStyle} value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} placeholder="e.g. Chapter 3 Notes — Photosynthesis" />
        </div>
        <div>
          <label style={labelStyle}>Description</label>
          <textarea style={{ ...inputStyle, resize: 'vertical' }} rows={3} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} placeholder="Brief description of this resource…" />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
          <div>
            <label style={labelStyle}>Grade</label>
            <select style={inputStyle} value={form.grade} onChange={e => setForm({ ...form, grade: Number(e.target.value) })}>
              {[1,2,3,4,5,6,7,8,9,10].map(g => <option key={g} value={g}>Grade {g}</option>)}
            </select>
          </div>
          <div>
            <label style={labelStyle}>Subject</label>
            <select style={inputStyle} value={form.subject} onChange={e => setForm({ ...form, subject: e.target.value })}>
              {Object.entries(SUBJECT_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
          <div>
            <label style={labelStyle}>Chapter</label>
            <input style={inputStyle} value={form.chapter} onChange={e => setForm({ ...form, chapter: e.target.value })} placeholder="e.g. Chapter 3" />
          </div>
          <div>
            <label style={labelStyle}>Type</label>
            <select style={inputStyle} value={form.resource_type} onChange={e => setForm({ ...form, resource_type: e.target.value })}>
              {[['pdf', 'PDF'], ['video', 'Video'], ['lesson', 'Lesson'], ['notes', 'Notes']].map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
        </div>
        <div>
          <label style={labelStyle}>File</label>
          <input type="file" onChange={e => setFile(e.target.files[0])} style={{ ...inputStyle, padding: '8px 14px' }} />
        </div>

        {message && (
          <div style={{ padding: '12px 16px', borderRadius: 9, background: message === 'success' ? '#f0fdf4' : '#fef2f2', color: message === 'success' ? '#166534' : '#991b1b', fontWeight: 600, fontSize: 14 }}>
            {message === 'success' ? '✅ Resource uploaded successfully!' : `❌ ${message.replace('error:', '')}`}
          </div>
        )}

        <button
          type="submit"
          disabled={submitting}
          style={{ background: submitting ? '#e2e8f0' : 'linear-gradient(135deg, #059669, #047857)', color: submitting ? '#94a3b8' : '#fff', border: 'none', borderRadius: 10, padding: '12px 0', fontWeight: 700, fontSize: 15, cursor: submitting ? 'default' : 'pointer' }}
        >
          {submitting ? 'Uploading…' : 'Upload Resource'}
        </button>
      </form>
    </div>
  );
};

/* ── Marks Upload ─────────────────────────────────────────────────────────── */

const MarksUpload = () => {
  const [grade, setGrade] = useState(5);
  const [subject, setSubject] = useState('maths');
  const [marks, setMarks] = useState([{ student_id: '', marks: '' }]);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const addRow = () => setMarks([...marks, { student_id: '', marks: '' }]);
  const updateRow = (i, field, val) => {
    const m = [...marks]; m[i][field] = val; setMarks(m);
  };
  const removeRow = (i) => setMarks(marks.filter((_, j) => j !== i));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage('');
    try {
      await api.post('/notifications/marks-upload/', { grade, subject, marks_data: marks.filter(m => m.student_id && m.marks) });
      setMessage('success');
      setMarks([{ student_id: '', marks: '' }]);
    } catch (e) {
      setMessage('error:' + (e.response?.data?.detail || e.message));
    } finally { setSubmitting(false); }
  };

  const inputStyle = { padding: '9px 12px', border: '1.5px solid #e2e8f0', borderRadius: 8, fontSize: 14, color: '#1e293b', outline: 'none', width: '100%', boxSizing: 'border-box' };
  const labelStyle = { display: 'block', fontSize: 12, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 };

  return (
    <div style={{ background: '#fff', borderRadius: 14, border: '1px solid #e5ebf3', boxShadow: '0 2px 8px rgba(13,38,76,0.05)', maxWidth: 700, padding: '28px 32px' }}>
      <h2 style={{ fontWeight: 800, color: '#0f3460', fontSize: '1.2rem', marginBottom: 24 }}>📝 Upload Student Marks</h2>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
          <div>
            <label style={labelStyle}>Grade</label>
            <select style={inputStyle} value={grade} onChange={e => setGrade(Number(e.target.value))}>
              {[1,2,3,4,5,6,7,8,9,10].map(g => <option key={g} value={g}>Grade {g}</option>)}
            </select>
          </div>
          <div>
            <label style={labelStyle}>Subject</label>
            <select style={inputStyle} value={subject} onChange={e => setSubject(e.target.value)}>
              {Object.entries(SUBJECT_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
        </div>

        <div>
          <label style={labelStyle}>Student Marks</label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {marks.map((m, i) => (
              <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 100px 80px', gap: 8 }}>
                <input placeholder="Student ID or username" value={m.student_id} onChange={e => updateRow(i, 'student_id', e.target.value)} style={inputStyle} />
                <input type="number" placeholder="Marks" value={m.marks} onChange={e => updateRow(i, 'marks', e.target.value)} style={inputStyle} />
                <button type="button" onClick={() => removeRow(i)} style={{ background: '#fef2f2', color: '#991b1b', border: '1.5px solid #fecaca', borderRadius: 8, cursor: marks.length > 1 ? 'pointer' : 'default', opacity: marks.length > 1 ? 1 : 0.4, fontWeight: 600, fontSize: 13 }} disabled={marks.length <= 1}>
                  Remove
                </button>
              </div>
            ))}
          </div>
          <button type="button" onClick={addRow} style={{ marginTop: 10, background: 'transparent', border: 'none', color: '#0084d1', cursor: 'pointer', fontWeight: 600, fontSize: 14 }}>
            + Add Student
          </button>
        </div>

        {message && (
          <div style={{ padding: '12px 16px', borderRadius: 9, background: message === 'success' ? '#f0fdf4' : '#fef2f2', color: message === 'success' ? '#166534' : '#991b1b', fontWeight: 600, fontSize: 14 }}>
            {message === 'success' ? '✅ Marks uploaded & SMS sent!' : `❌ ${message.replace('error:', '')}`}
          </div>
        )}

        <button
          type="submit"
          disabled={submitting}
          style={{ background: submitting ? '#e2e8f0' : 'linear-gradient(135deg, #7c3aed, #6d28d9)', color: submitting ? '#94a3b8' : '#fff', border: 'none', borderRadius: 10, padding: '12px 0', fontWeight: 700, fontSize: 15, cursor: submitting ? 'default' : 'pointer' }}
        >
          {submitting ? 'Uploading…' : 'Upload Marks & Send SMS'}
        </button>
      </form>
    </div>
  );
};
