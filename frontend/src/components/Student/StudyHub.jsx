import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';

/**
 * Smart Study Hub
 *
 * Flow:
 *   1. Student picks: grade, syllabus, subject, chapter, language
 *   2. They click "Generate Lesson"
 *   3. We POST to /api/study-hub/generate/
 *   4. Backend either returns a cached lesson, or asks Ollama to make one (~10s)
 *   5. We display: Summary (markdown) + Key Points (bullet list)
 */

const SUBJECTS = [
  'Mathematics', 'Science', 'English', 'Hindi', 'Social Science',
  'Computer Science', 'History', 'Geography', 'Civics', 'Economics',
];

const SYLLABI = [
  { value: 'CBSE', label: 'CBSE' },
  { value: 'ICSE', label: 'ICSE' },
  { value: 'KARNATAKA', label: 'Karnataka State Board' },
  { value: 'MAHARASHTRA', label: 'Maharashtra State Board' },
  { value: 'TAMILNADU', label: 'Tamil Nadu State Board' },
  { value: 'WESTBENGAL', label: 'West Bengal State Board' },
  { value: 'ANDHRAPRADESH', label: 'Andhra Pradesh State Board' },
];

const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'hi', label: 'हिन्दी (Hindi)' },
  { value: 'ta', label: 'தமிழ் (Tamil)' },
  { value: 'te', label: 'తెలుగు (Telugu)' },
  { value: 'bn', label: 'বাংলা (Bengali)' },
  { value: 'kn', label: 'ಕನ್ನಡ (Kannada)' },
  { value: 'mr', label: 'मराठी (Marathi)' },
];

export const StudyHub = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  // Form state
  const [form, setForm] = useState({
    grade: user?.grade || 5,
    syllabus: 'CBSE',
    subject: 'Mathematics',
    chapter: '',
    language: 'en',
  });

  const [lesson, setLesson] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [recent, setRecent] = useState([]);

  // Load recent lessons when the page opens
  useEffect(() => {
    api.get('/study-hub/recent/')
      .then(r => setRecent(r.data || []))
      .catch(() => setRecent([]));
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!form.chapter.trim()) {
      setError('Please enter a chapter name');
      return;
    }
    setError('');
    setLoading(true);
    setLesson(null);

    try {
      const res = await api.post('/study-hub/generate/', {
        ...form,
        grade: parseInt(form.grade),
      });
      setLesson(res.data);
      // Refresh recent list
      const r = await api.get('/study-hub/recent/');
      setRecent(r.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate. Is Ollama running?');
    } finally {
      setLoading(false);
    }
  };

  const openCached = (cachedLesson) => setLesson(cachedLesson);

  return (
    <div className="prof-page-shell">
      <header className="prof-page-header">
        <div className="prof-page-header-inner">
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <button
              onClick={() => navigate('/dashboard')}
              style={{ color: '#7dd3fc', background: 'transparent', border: 'none', cursor: 'pointer', fontWeight: 600 }}
            >
              ← Back
            </button>
            <div>
              <h1 className="prof-page-title">📖 Smart Study Hub</h1>
              <p className="prof-page-subtitle">
                Get instant lesson summaries powered by AI — in your language
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="prof-main">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          {/* LEFT: form + recent */}
          <div>
            <div className="prof-surface" style={{ padding: 24, marginBottom: 16 }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f3460', marginBottom: 16 }}>
                Pick a chapter
              </h2>
              <form onSubmit={handleGenerate} style={{ display: 'grid', gap: 12 }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  <Field label="Grade">
                    <select name="grade" value={form.grade} onChange={handleChange} style={inputStyle}>
                      {[1,2,3,4,5,6,7,8,9,10].map(g => <option key={g} value={g}>Grade {g}</option>)}
                    </select>
                  </Field>
                  <Field label="Language">
                    <select name="language" value={form.language} onChange={handleChange} style={inputStyle}>
                      {LANGUAGES.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
                    </select>
                  </Field>
                </div>

                <Field label="Syllabus / Board">
                  <select name="syllabus" value={form.syllabus} onChange={handleChange} style={inputStyle}>
                    {SYLLABI.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                  </select>
                </Field>

                <Field label="Subject">
                  <select name="subject" value={form.subject} onChange={handleChange} style={inputStyle}>
                    {SUBJECTS.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </Field>

                <Field label="Chapter Name">
                  <input
                    type="text"
                    name="chapter"
                    value={form.chapter}
                    onChange={handleChange}
                    placeholder="e.g. Integers, Photosynthesis, French Revolution"
                    style={inputStyle}
                  />
                </Field>

                {error && (
                  <div style={{ background: '#fee', color: '#c33', padding: 10, borderRadius: 8, fontSize: 13 }}>
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="prof-action-btn prof-action-btn-primary"
                  style={{ padding: '12px', fontSize: 15, opacity: loading ? 0.6 : 1 }}
                >
                  {loading ? 'Generating lesson… (this can take ~10 seconds)' : '✨ Generate Lesson'}
                </button>
              </form>
            </div>

            {/* Recent lessons */}
            {recent.length > 0 && (
              <div className="prof-surface" style={{ padding: 20 }}>
                <h3 style={{ fontWeight: 700, color: '#0f3460', marginBottom: 12, fontSize: '1rem' }}>
                  📚 Recent Lessons
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {recent.map(r => (
                    <button
                      key={r.id}
                      onClick={() => openCached(r)}
                      style={{
                        textAlign: 'left',
                        padding: 10,
                        background: '#f8fafc',
                        border: '1px solid #e5ebf3',
                        borderRadius: 8,
                        cursor: 'pointer',
                        fontSize: 13,
                      }}
                    >
                      <div style={{ fontWeight: 600, color: '#0f3460' }}>{r.chapter}</div>
                      <div style={{ color: '#64748b', fontSize: 12 }}>
                        Grade {r.grade} · {r.subject} · {r.syllabus}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* RIGHT: lesson display */}
          <div>
            {!lesson && !loading && (
              <div className="prof-surface" style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>
                <div style={{ fontSize: '3rem', marginBottom: 12 }}>📚</div>
                <p style={{ fontWeight: 600, color: '#0f3460' }}>Your lesson will appear here</p>
                <p style={{ fontSize: 13, marginTop: 6 }}>
                  Pick a chapter on the left and click <strong>Generate Lesson</strong>.
                </p>
              </div>
            )}

            {loading && (
              <div className="prof-surface" style={{ padding: 40, textAlign: 'center' }}>
                <div className="animate-spin" style={{
                  width: 40, height: 40, margin: '0 auto',
                  border: '3px solid #e5ebf3', borderTopColor: '#0084d1',
                  borderRadius: '50%',
                }}></div>
                <p style={{ marginTop: 16, color: '#64748b' }}>
                  Asking the AI to write your lesson…
                </p>
              </div>
            )}

            {lesson && (
              <div className="prof-surface" style={{ padding: 28 }}>
                <div style={{ marginBottom: 16, paddingBottom: 16, borderBottom: '1px solid #e5ebf3' }}>
                  <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f3460' }}>
                    {lesson.chapter}
                  </h2>
                  <p style={{ color: '#64748b', fontSize: 13, marginTop: 4 }}>
                    Grade {lesson.grade} · {lesson.subject} · {lesson.syllabus}
                  </p>
                </div>

                {/* Key points (bullets) */}
                {lesson.key_points && lesson.key_points.length > 0 && (
                  <div style={{
                    background: '#e0f6ff', borderRadius: 10, padding: 16, marginBottom: 16,
                  }}>
                    <h3 style={{ fontWeight: 700, color: '#0084d1', marginBottom: 8, fontSize: 14 }}>
                      🎯 Key Takeaways
                    </h3>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                      {lesson.key_points.map((kp, i) => (
                        <li key={i} style={{ padding: '4px 0', color: '#1e3a8a', fontSize: 14 }}>
                          ✓ {kp}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Full summary - rendered as preformatted markdown */}
                <div style={{
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'system-ui, -apple-system, sans-serif',
                  fontSize: 15,
                  lineHeight: 1.65,
                  color: '#1e293b',
                }}>
                  {lesson.summary}
                </div>

                <div style={{ marginTop: 20, display: 'flex', gap: 8 }}>
                  <button
                    onClick={() => navigate('/tutor', { state: { chapter: lesson.chapter, subject: lesson.subject, grade: lesson.grade, syllabus: lesson.syllabus, language: lesson.language } })}
                    className="prof-action-btn prof-action-btn-primary"
                    style={{ padding: '10px 16px', fontSize: 14 }}
                  >
                    💬 Ask the Tutor about this chapter
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

const Field = ({ label, children }) => (
  <div>
    <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: '#334155', marginBottom: 4 }}>
      {label}
    </label>
    {children}
  </div>
);

const inputStyle = {
  width: '100%',
  padding: '10px 12px',
  border: '1px solid #cbd5e1',
  borderRadius: 8,
  fontSize: 14,
  fontFamily: 'inherit',
  outline: 'none',
};
