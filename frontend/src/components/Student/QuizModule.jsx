import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { subscribeToQuizzes, getQuizById, recordQuizAttempt } from '../../services/firestoreService';

const SUBJECT_STYLES = {
  maths:         { color: '#2563eb', bg: '#eff6ff', badge: '#bfdbfe' },
  science:       { color: '#059669', bg: '#f0fdf4', badge: '#bbf7d0' },
  english:       { color: '#0891b2', bg: '#ecfeff', badge: '#a5f3fc' },
  kannada:       { color: '#7c3aed', bg: '#f5f3ff', badge: '#ddd6fe' },
  social_science:{ color: '#d97706', bg: '#fffbeb', badge: '#fde68a' },
  hindi:         { color: '#dc2626', bg: '#fef2f2', badge: '#fecaca' },
  marathi:       { color: '#db2777', bg: '#fdf2f8', badge: '#fbcfe8' },
};

const SUBJECT_LABELS = {
  maths: 'Mathematics', science: 'Science', english: 'English',
  kannada: 'Kannada', social_science: 'Social Science',
  hindi: 'Hindi', marathi: 'Marathi',
};

const SUBJECTS = [
  { value: 'all', label: 'All Subjects' },
  { value: 'kannada', label: 'Kannada' },
  { value: 'hindi', label: 'Hindi' },
  { value: 'marathi', label: 'Marathi' },
  { value: 'english', label: 'English' },
  { value: 'maths', label: 'Mathematics' },
  { value: 'science', label: 'Science' },
  { value: 'social_science', label: 'Social Science' },
];

// A quiz is treated as a Past-Year Paper if its title starts with this prefix
const isPYQ = (quiz) => (quiz?.title || '').startsWith('Past Year Paper');

export const QuizModule = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [quizzes, setQuizzes] = useState([]);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSubject, setSelectedSubject] = useState('all');
  const [selectedGrade, setSelectedGrade] = useState(user?.grade || 5);
  const [quizMode, setQuizMode] = useState('chapter'); // 'chapter' | 'pyq'

  useEffect(() => {
    setLoading(true);
    const unsubscribe = subscribeToQuizzes(
      { grade: selectedGrade, subject: selectedSubject !== 'all' ? selectedSubject : undefined },
      (items) => {
        setQuizzes(items);
        setLoading(false);
      }
    );
    return () => unsubscribe?.();
  }, [selectedGrade, selectedSubject]);

  // Split into chapter quizzes vs PYQ papers
  const pyqQuizzes = quizzes.filter(isPYQ);
  const chapterQuizzes = quizzes.filter(q => !isPYQ(q));
  const activeList = quizMode === 'pyq' ? pyqQuizzes : chapterQuizzes;

  const filtered = selectedSubject === 'all'
    ? activeList
    : activeList.filter(q => q.subject === selectedSubject);

  if (selectedQuiz) {
    return (
      <QuizTaker
        quiz={selectedQuiz}
        onComplete={() => { setSelectedQuiz(null); fetchQuizzes(); }}
        onBack={() => setSelectedQuiz(null)}
      />
    );
  }

  return (
    <div className="prof-page-shell">
      <header className="prof-page-header">
        <div className="prof-page-header-inner" style={{ flexDirection: 'column', alignItems: 'stretch', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <button
              onClick={() => navigate('/dashboard')}
              style={{ background: 'rgba(255,255,255,0.12)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff', borderRadius: 8, padding: '6px 14px', cursor: 'pointer', fontWeight: 600, fontSize: 14 }}
            >
              ← Back
            </button>
            <div>
              <h1 className="prof-page-title">
                {quizMode === 'pyq' ? '📄 Past Year Papers' : '📝 Quizzes'}
              </h1>
              <p className="prof-page-subtitle">
                {quizMode === 'pyq'
                  ? 'Mock board-style papers covering full syllabus'
                  : 'Chapter-wise assessments to track your progress'}
              </p>
            </div>
          </div>

          {/* Mode tabs: Chapter Quizzes vs Past Year Papers */}
          <div style={{ display: 'flex', gap: 6, padding: 4, background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 10, width: 'fit-content' }}>
            {[
              { key: 'chapter', icon: '📝', label: 'Chapter Quizzes', count: chapterQuizzes.length },
              { key: 'pyq',     icon: '📄', label: 'Past Year Papers', count: pyqQuizzes.length },
            ].map(t => {
              const active = quizMode === t.key;
              return (
                <button
                  key={t.key}
                  onClick={() => setQuizMode(t.key)}
                  style={{
                    padding: '8px 16px',
                    borderRadius: 8,
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: 14,
                    fontWeight: active ? 700 : 500,
                    background: active ? '#fff' : 'transparent',
                    color: active ? '#0f3460' : 'rgba(255,255,255,0.85)',
                    transition: 'all 0.15s',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                  }}
                >
                  <span>{t.icon}</span>
                  <span>{t.label}</span>
                  <span style={{
                    background: active ? '#e0e7ff' : 'rgba(255,255,255,0.18)',
                    color: active ? '#0f3460' : '#fff',
                    padding: '2px 8px',
                    borderRadius: 10,
                    fontSize: 11,
                    fontWeight: 700,
                  }}>{t.count}</span>
                </button>
              );
            })}
          </div>
        </div>
      </header>

      <main className="prof-main">
        {/* Filters */}
        <div className="prof-surface" style={{ padding: '20px 24px', marginBottom: 24 }}>
          <div style={{ display: 'flex', gap: 16, alignItems: 'flex-end', flexWrap: 'wrap' }}>
            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#64748b', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Grade</label>
              <select
                value={selectedGrade}
                onChange={e => setSelectedGrade(Number(e.target.value))}
                style={{ padding: '8px 12px', border: '1px solid #cbd5e1', borderRadius: 8, fontSize: 14, color: '#1e293b', background: '#fff', cursor: 'pointer' }}
              >
                {[1,2,3,4,5,6,7,8,9,10].map(g => <option key={g} value={g}>Grade {g}</option>)}
              </select>
            </div>
            <div style={{ flex: 1, minWidth: 200 }}>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#64748b', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Subject</label>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {SUBJECTS.map(s => {
                  const style = s.value !== 'all' ? SUBJECT_STYLES[s.value] : null;
                  const active = selectedSubject === s.value;
                  return (
                    <button
                      key={s.value}
                      onClick={() => setSelectedSubject(s.value)}
                      style={{
                        padding: '6px 14px',
                        borderRadius: 20,
                        fontSize: 13,
                        fontWeight: active ? 700 : 500,
                        cursor: 'pointer',
                        border: active ? '2px solid ' + (style?.color || '#0f3460') : '1px solid #e2e8f0',
                        background: active ? (style?.bg || '#f0f4f8') : '#fff',
                        color: active ? (style?.color || '#0f3460') : '#64748b',
                        transition: 'all 0.15s',
                      }}
                    >
                      {s.label}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '60px 0' }}>
            <div style={{ width: 40, height: 40, border: '3px solid #e2e8f0', borderTopColor: '#0084d1', borderRadius: '50%', margin: '0 auto', animation: 'spin 0.8s linear infinite' }} />
            <p style={{ color: '#64748b', marginTop: 16 }}>Loading quizzes…</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="prof-surface" style={{ padding: '60px 20px', textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', marginBottom: 12 }}>{quizMode === 'pyq' ? '📄' : '📋'}</div>
            <p style={{ color: '#64748b', fontSize: 16 }}>
              {quizMode === 'pyq'
                ? 'No past year papers found for this grade and subject.'
                : 'No quizzes found for this grade and subject.'}
            </p>
            <p style={{ color: '#94a3b8', fontSize: 13, marginTop: 6 }}>Try a different grade or subject filter.</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 20 }}>
            {filtered.map(quiz => <QuizCard key={quiz.id} quiz={quiz} onStart={() => setSelectedQuiz(quiz)} isPyq={isPYQ(quiz)} />)}
          </div>
        )}
      </main>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

const QuizCard = ({ quiz, onStart, isPyq = false }) => {
  const style = SUBJECT_STYLES[quiz.subject] || SUBJECT_STYLES.maths;
  const [hovered, setHovered] = useState(false);

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        background: '#fff',
        borderRadius: 14,
        boxShadow: hovered ? '0 8px 24px rgba(13,38,76,0.12)' : '0 2px 8px rgba(13,38,76,0.06)',
        border: isPyq ? '2px solid #0f3460' : '1px solid #e5ebf3',
        overflow: 'hidden',
        transition: 'box-shadow 0.2s, transform 0.2s',
        transform: hovered ? 'translateY(-3px)' : 'none',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
      }}
    >
      {/* PYQ ribbon */}
      {isPyq && (
        <div style={{
          position: 'absolute',
          top: 12,
          right: -28,
          background: 'linear-gradient(135deg, #0f3460 0%, #16213e 100%)',
          color: '#fff',
          fontSize: 10,
          fontWeight: 700,
          letterSpacing: '0.08em',
          padding: '3px 32px',
          transform: 'rotate(35deg)',
          boxShadow: '0 2px 4px rgba(0,0,0,0.15)',
          zIndex: 1,
        }}>
          MOCK
        </div>
      )}

      {/* Colored top bar */}
      <div style={{ height: 5, background: isPyq ? 'linear-gradient(90deg, #0f3460, #16213e)' : style.color }} />

      <div style={{ padding: '18px 20px', flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Subject + Grade badges */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <span style={{
            background: style.bg,
            color: style.color,
            border: `1px solid ${style.badge}`,
            padding: '3px 10px',
            borderRadius: 20,
            fontSize: 11,
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}>
            {SUBJECT_LABELS[quiz.subject] || quiz.subject}
          </span>
          <span style={{ background: '#f1f5f9', color: '#64748b', padding: '3px 8px', borderRadius: 6, fontSize: 12, fontWeight: 600 }}>
            Gr. {quiz.grade}
          </span>
        </div>

        {/* Title */}
        <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1e293b', marginBottom: 6, lineHeight: 1.4, flex: 1 }}>
          {quiz.title}
        </h3>
        <p style={{ fontSize: 12, color: '#94a3b8', marginBottom: 14, lineHeight: 1.4, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
          {quiz.description || 'Chapter practice assessment'}
        </p>

        {/* Stats grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6, marginBottom: 16 }}>
          {[
            ['❓', `${quiz.num_questions || 0} Qs`],
            ['⏱️', `${quiz.duration_minutes || 30} min`],
            ['📊', quiz.avg_score ? `Avg ${Math.round(quiz.avg_score)}%` : 'New'],
            ['🎯', `Pass ${Math.round(quiz.passing_percentage || 40)}%`],
          ].map(([icon, text]) => (
            <div key={text} style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 12, color: '#475569' }}>
              <span>{icon}</span><span>{text}</span>
            </div>
          ))}
        </div>

        {/* CTA button */}
        <button
          onClick={onStart}
          style={{
            width: '100%',
            background: `linear-gradient(135deg, ${style.color}, ${style.color}dd)`,
            color: '#fff',
            border: 'none',
            borderRadius: 8,
            padding: '10px 0',
            fontWeight: 700,
            fontSize: 14,
            cursor: 'pointer',
          }}
        >
          Start Quiz →
        </button>
      </div>
    </div>
  );
};

const QuizTaker = ({ quiz, onComplete, onBack }) => {
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  const style = SUBJECT_STYLES[quiz.subject] || SUBJECT_STYLES.maths;

  useEffect(() => { loadQuiz(); }, []);

  const loadQuiz = async () => {
    try {
      const res = await api.get(`/quizzes/${quiz.id}/`);
      setQuestions(res.data.questions || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = (qId, key) => setAnswers(prev => ({ ...prev, [qId]: key }));

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const res = await api.post(`/quizzes/${quiz.id}/submit/`, { answers_json: answers });
      setResult(res.data);
    } catch (e) {
      console.error(e);
      alert('Failed to submit quiz. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: '#f3f6fb', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 16 }}>
        <div style={{ width: 44, height: 44, border: '3px solid #e2e8f0', borderTopColor: style.color, borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
        <p style={{ color: '#64748b' }}>Loading quiz…</p>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (result) {
    const pct = Math.round(result.percentage);
    const passed = result.passed;
    const emoji = pct >= 90 ? '🏆' : pct >= 75 ? '🎉' : pct >= 50 ? '👍' : '📚';
    const grade = pct >= 90 ? 'Excellent!' : pct >= 75 ? 'Great Job!' : pct >= 50 ? 'Good Effort!' : 'Keep Practising!';
    const scoreColor = pct >= 75 ? '#059669' : pct >= 50 ? '#d97706' : '#dc2626';

    return (
      <div style={{ minHeight: '100vh', background: '#f3f6fb', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
        <div style={{ background: '#fff', borderRadius: 20, boxShadow: '0 8px 32px rgba(13,38,76,0.12)', maxWidth: 440, width: '100%', padding: '48px 40px', textAlign: 'center' }}>
          <div style={{ fontSize: '4rem', marginBottom: 8 }}>{emoji}</div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f3460', marginBottom: 4 }}>{grade}</h2>
          <p style={{ color: '#64748b', fontSize: 14, marginBottom: 32 }}>{quiz.title}</p>

          {/* Score circle */}
          <div style={{ width: 120, height: 120, borderRadius: '50%', border: `6px solid ${scoreColor}`, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px' }}>
            <span style={{ fontSize: '2rem', fontWeight: 800, color: scoreColor, lineHeight: 1 }}>{pct}%</span>
            <span style={{ fontSize: 12, color: '#94a3b8' }}>Score</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 32 }}>
            {[
              ['Marks', `${result.score} / ${result.total_marks}`],
              ['Status', passed ? '✓ Passed' : '✗ Failed'],
            ].map(([label, value]) => (
              <div key={label} style={{ background: '#f8fafc', borderRadius: 10, padding: '12px', border: '1px solid #e5ebf3' }}>
                <div style={{ fontSize: 11, color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase', marginBottom: 4 }}>{label}</div>
                <div style={{ fontSize: 16, fontWeight: 700, color: label === 'Status' ? (passed ? '#059669' : '#dc2626') : '#1e293b' }}>{value}</div>
              </div>
            ))}
          </div>

          <button
            onClick={onComplete}
            style={{ width: '100%', background: `linear-gradient(135deg, ${style.color}, ${style.color}cc)`, color: '#fff', border: 'none', borderRadius: 10, padding: '13px 0', fontWeight: 700, fontSize: 15, cursor: 'pointer' }}
          >
            ← Back to Quizzes
          </button>
        </div>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div style={{ minHeight: '100vh', background: '#f3f6fb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ background: '#fff', borderRadius: 16, padding: '40px 32px', textAlign: 'center', boxShadow: '0 4px 16px rgba(13,38,76,0.08)' }}>
          <div style={{ fontSize: '3rem', marginBottom: 12 }}>⚠️</div>
          <p style={{ color: '#64748b', marginBottom: 20 }}>No questions available for this quiz yet.</p>
          <button onClick={onBack} style={{ background: '#f1f5f9', color: '#475569', border: 'none', borderRadius: 8, padding: '10px 20px', cursor: 'pointer', fontWeight: 600 }}>← Go Back</button>
        </div>
      </div>
    );
  }

  const q = questions[currentIndex];
  const progress = ((currentIndex + 1) / questions.length) * 100;
  const allAnswered = questions.every(q => answers[q.id] !== undefined);
  const options = Array.isArray(q.options) ? q.options : [];

  return (
    <div style={{ minHeight: '100vh', background: '#f3f6fb' }}>
      {/* Header */}
      <div style={{ background: '#fff', borderBottom: '1px solid #e5ebf3', padding: '0 0 0 0' }}>
        <div style={{ maxWidth: 780, margin: '0 auto', padding: '14px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button onClick={onBack} style={{ background: '#f1f5f9', border: 'none', borderRadius: 6, padding: '5px 12px', cursor: 'pointer', color: '#475569', fontWeight: 600, fontSize: 13 }}>← Back</button>
            <div>
              <div style={{ fontWeight: 700, fontSize: 15, color: '#1e293b' }}>{quiz.title}</div>
              <div style={{ fontSize: 12, color: '#94a3b8' }}>{SUBJECT_LABELS[quiz.subject] || quiz.subject} · Grade {quiz.grade}</div>
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 13, color: '#64748b' }}>Question</div>
            <div style={{ fontWeight: 800, fontSize: 18, color: style.color }}>{currentIndex + 1}<span style={{ color: '#94a3b8', fontWeight: 400, fontSize: 14 }}> / {questions.length}</span></div>
          </div>
        </div>
        {/* Progress bar */}
        <div style={{ height: 4, background: '#e5ebf3' }}>
          <div style={{ height: '100%', width: `${progress}%`, background: `linear-gradient(90deg, ${style.color}, ${style.color}cc)`, transition: 'width 0.3s' }} />
        </div>
      </div>

      {/* Question */}
      <div style={{ maxWidth: 780, margin: '0 auto', padding: '32px 20px' }}>
        <div style={{ background: '#fff', borderRadius: 16, boxShadow: '0 2px 12px rgba(13,38,76,0.07)', border: '1px solid #e5ebf3', padding: '32px', marginBottom: 20 }}>

          {/* Question number badge */}
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: style.bg, color: style.color, borderRadius: 20, padding: '4px 12px', fontSize: 12, fontWeight: 700, marginBottom: 16 }}>
            Q{currentIndex + 1}
          </div>

          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#1e293b', marginBottom: 24, lineHeight: 1.5 }}>
            {q.question_text}
          </h2>

          {/* Options */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {options.map((opt, idx) => {
              const optKey = typeof opt === 'string' ? opt : (opt.key || `option_${idx}`);
              const optText = typeof opt === 'string' ? opt : (opt.text || String(opt));
              const isSelected = answers[q.id] === optKey;
              const letter = String.fromCharCode(65 + idx);

              return (
                <button
                  key={idx}
                  onClick={() => handleAnswer(q.id, optKey)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 14,
                    padding: '14px 18px',
                    borderRadius: 10,
                    border: isSelected ? `2px solid ${style.color}` : '1.5px solid #e2e8f0',
                    background: isSelected ? style.bg : '#fff',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.15s',
                    boxShadow: isSelected ? `0 0 0 3px ${style.badge}` : 'none',
                  }}
                >
                  <span style={{
                    minWidth: 32, height: 32,
                    borderRadius: '50%',
                    background: isSelected ? style.color : '#f1f5f9',
                    color: isSelected ? '#fff' : '#64748b',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 700, fontSize: 13, flexShrink: 0,
                  }}>
                    {letter}
                  </span>
                  <span style={{ fontSize: 14, color: isSelected ? style.color : '#334155', fontWeight: isSelected ? 600 : 400 }}>
                    {optText}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Navigation */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 28 }}>
            <button
              onClick={() => setCurrentIndex(i => Math.max(0, i - 1))}
              disabled={currentIndex === 0}
              style={{ padding: '10px 20px', borderRadius: 8, border: '1.5px solid #e2e8f0', background: '#fff', color: currentIndex === 0 ? '#cbd5e1' : '#475569', cursor: currentIndex === 0 ? 'default' : 'pointer', fontWeight: 600, fontSize: 14 }}
            >
              ← Previous
            </button>

            {currentIndex < questions.length - 1 ? (
              <button
                onClick={() => setCurrentIndex(i => i + 1)}
                style={{ padding: '10px 24px', borderRadius: 8, border: 'none', background: `linear-gradient(135deg, ${style.color}, ${style.color}cc)`, color: '#fff', cursor: 'pointer', fontWeight: 700, fontSize: 14 }}
              >
                Next →
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={!allAnswered || submitting}
                style={{ padding: '10px 24px', borderRadius: 8, border: 'none', background: allAnswered && !submitting ? 'linear-gradient(135deg, #059669, #047857)' : '#e2e8f0', color: allAnswered && !submitting ? '#fff' : '#94a3b8', cursor: allAnswered && !submitting ? 'pointer' : 'default', fontWeight: 700, fontSize: 14, transition: 'all 0.15s' }}
              >
                {submitting ? 'Submitting…' : '✓ Submit Quiz'}
              </button>
            )}
          </div>
        </div>

        {/* Question navigator */}
        <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
          {questions.map((question, idx) => {
            const answered = answers[question.id] !== undefined;
            const isCurrent = idx === currentIndex;
            return (
              <button
                key={question.id}
                onClick={() => setCurrentIndex(idx)}
                style={{
                  width: 36, height: 36,
                  borderRadius: '50%',
                  border: isCurrent ? `2px solid ${style.color}` : answered ? '1.5px solid #86efac' : '1.5px solid #e2e8f0',
                  background: isCurrent ? style.color : answered ? '#f0fdf4' : '#fff',
                  color: isCurrent ? '#fff' : answered ? '#059669' : '#64748b',
                  fontSize: 13,
                  fontWeight: 700,
                  cursor: 'pointer',
                }}
              >
                {idx + 1}
              </button>
            );
          })}
        </div>

        {!allAnswered && (
          <p style={{ textAlign: 'center', color: '#94a3b8', fontSize: 12, marginTop: 12 }}>
            Answer all {questions.length} questions to submit
          </p>
        )}
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};
