import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { subscribeToResources } from '../../services/firestoreService';

/* ── subject catalogue ─────────────────────────────────────────────────── */
const SUBJECTS = [
  { value: 'maths',          label: 'Mathematics',    icon: '📐',
    color: '#2563eb', dark: '#1d4ed8', light: '#eff6ff' },
  { value: 'science',        label: 'Science',        icon: '🔬',
    color: '#16a34a', dark: '#15803d', light: '#f0fdf4' },
  { value: 'english',        label: 'English',        icon: '📖',
    color: '#7c3aed', dark: '#6d28d9', light: '#f5f3ff' },
  { value: 'social_science', label: 'Social Science', icon: '🌍',
    color: '#ea580c', dark: '#c2410c', light: '#fff7ed' },
  { value: 'kannada',        label: 'Kannada',        icon: '🅺',
    color: '#dc2626', dark: '#b91c1c', light: '#fef2f2' },
];

const openLink = (url) => window.open(url, '_blank', 'noopener,noreferrer');

/* ═══════════════════════════════════════════════════════════════════════════
   ROOT
═══════════════════════════════════════════════════════════════════════════ */
export const ResourceBrowser = () => {
  const navigate = useNavigate();
  const { user }  = useAuth();

  const [grade, setGrade] = useState(user?.grade || 5);
  const [subject, setSubject] = useState(null);
  const [resources, setResources] = useState([]);
  const [loadingResources, setLoadingResources] = useState(false);

  useEffect(() => {
    if (!subject) return undefined;

    setLoadingResources(true);
    const unsubscribe = subscribeToResources({ grade, subject: subject.value }, (items) => {
      setResources(items);
      setLoadingResources(false);
    });

    return () => unsubscribe?.();
  }, [grade, subject]);

  if (!subject) {
    return (
      <div className="prof-page-shell">
        <PageHeader onBack={() => navigate('/dashboard')} title="Learning Resources" />
        <main className="prof-main">
          <div className="prof-surface" style={{ marginBottom: 24 }}>
            <p className="prof-section-subtitle">Choose a grade and subject to browse resources stored in Firebase.</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, marginTop: 18 }}>
              {[1,2,3,4,5,6,7,8,9,10].map(g => (
                <button
                  key={g}
                  onClick={() => setGrade(g)}
                  className={`px-4 py-2 rounded-full font-semibold transition ${grade === g ? 'bg-cyan-600 text-white shadow-lg' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}`}
                >
                  Grade {g}
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginTop: 16 }}>
            <p className="prof-section-title">Pick a Subject</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
              {SUBJECTS.map(s => (
                <button
                  key={s.value}
                  onClick={() => setSubject(s)}
                  className="prof-surface hover:scale-[1.02] transition-transform"
                  style={{
                    background: `linear-gradient(135deg, ${s.color}, ${s.dark})`,
                    color: '#fff', border: 'none', minHeight: 160,
                    display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: '22px 24px',
                  }}
                >
                  <div style={{ fontSize: 40 }}>{s.icon}</div>
                  <div>
                    <div style={{ fontSize: 20, fontWeight: 800 }}>{s.label}</div>
                    <div style={{ marginTop: 6, opacity: 0.9 }}>Grade {grade}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="prof-page-shell">
      <PageHeader onBack={() => setSubject(null)} title={subject.label} />
      <main className="prof-main">
        <div className="prof-surface" style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <h2 style={{ fontSize: 22, fontWeight: 700, color: '#0f3460' }}>{subject.label} · Grade {grade}</h2>
            <p style={{ color: '#64748b', marginTop: 6 }}>Browse documents, videos and files uploaded to Firebase Storage.</p>
          </div>
          <button
            onClick={() => navigate('/quizzes')}
            className="prof-action-btn prof-action-btn-primary"
            style={{ alignSelf: 'center' }}
          >
            View Quizzes
          </button>
        </div>

        {loadingResources ? (
          <Spinner />
        ) : resources.length === 0 ? (
          <EmptyState text="No resources found for this grade and subject yet." />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {resources.map(resource => (
              <ResourceCard
                key={resource.id}
                icon={resource.resourceType === 'video' ? '🎥' : resource.resourceType === 'image' ? '🖼️' : '📄'}
                label={resource.resourceType?.toUpperCase() || 'PDF'}
                labelColor="#0f3460"
                labelBg="#e0f2fe"
                title={resource.title || resource.description || 'Learning Resource'}
                desc={resource.description || `${subject.label} resource for Grade ${grade}`}
                btnLabel="Open Resource"
                btnBg="#0f3460"
                onClick={() => resource.resourceUrl && openLink(resource.resourceUrl)}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

/* ── Sub-components ─────────────────────────────────────────────────────── */

const linkBtn = {
  background: 'none', border: 'none', color: '#0891b2',
  cursor: 'pointer', fontSize: 13, padding: 0, fontWeight: 500,
  textDecoration: 'underline',
};

const PageHeader = ({ onBack, title }) => (
  <header className="prof-page-header">
    <div className="prof-page-header-inner">
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <button onClick={onBack} style={{
          background: 'none', border: 'none', color: '#67e8f9',
          fontWeight: 700, fontSize: 15, cursor: 'pointer',
        }}>← Back</button>
        <div>
          <h1 className="prof-page-title">📚 {title}</h1>
          <p className="prof-page-subtitle">NCERT textbooks · videos · quizzes · all free</p>
        </div>
      </div>
    </div>
  </header>
);

const ChapterCard = ({ ch, subject, onClick }) => (
  <button onClick={onClick} style={{
    background: '#fff', border: '1.5px solid #e2e8f0',
    borderRadius: 12, padding: '16px 18px', textAlign: 'left',
    cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 14,
    boxShadow: '0 1px 4px rgba(0,0,0,.06)',
    transition: 'all .15s',
  }}
    onMouseEnter={e => { e.currentTarget.style.borderColor=subject.color; e.currentTarget.style.boxShadow=`0 4px 16px ${subject.color}22`; e.currentTarget.style.transform='translateY(-2px)'; }}
    onMouseLeave={e => { e.currentTarget.style.borderColor='#e2e8f0'; e.currentTarget.style.boxShadow='0 1px 4px rgba(0,0,0,.06)'; e.currentTarget.style.transform=''; }}
  >
    {/* number badge */}
    <div style={{
      minWidth: 40, height: 40, borderRadius: 10,
      background: subject.light, color: subject.color,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: 15, fontWeight: 800, flexShrink: 0,
    }}>{ch.number}</div>

    <div style={{ flex: 1, overflow: 'hidden' }}>
      <div style={{
        fontSize: 14, fontWeight: 600, color: '#1e293b',
        overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
      }}>{ch.title}</div>
      <div style={{ fontSize: 12, color: subject.color, marginTop: 3, fontWeight: 500 }}>
        View resources →
      </div>
    </div>
  </button>
);

const ResourceCard = ({ icon, label, labelColor, labelBg, title, desc, btnLabel, btnBg, onClick }) => (
  <div style={{
    background: '#fff', border: '1.5px solid #e2e8f0',
    borderRadius: 14, padding: '20px 20px 16px',
    display: 'flex', flexDirection: 'column', gap: 10,
    boxShadow: '0 1px 4px rgba(0,0,0,.06)',
  }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <span style={{ fontSize: 32 }}>{icon}</span>
      <span style={{
        fontSize: 11, fontWeight: 700, padding: '3px 10px', borderRadius: 999,
        background: labelBg, color: labelColor, letterSpacing: '.05em',
      }}>{label}</span>
    </div>
    <div>
      <div style={{ fontSize: 15, fontWeight: 700, color: '#1e293b' }}>{title}</div>
      <div style={{ fontSize: 12, color: '#64748b', marginTop: 4, lineHeight: 1.5 }}>{desc}</div>
    </div>
    <button onClick={onClick} style={{
      background: btnBg, color: '#fff', border: 'none',
      borderRadius: 8, padding: '10px 0', fontSize: 14,
      fontWeight: 600, cursor: 'pointer', marginTop: 'auto',
      transition: 'opacity .15s',
    }}
      onMouseEnter={e => e.currentTarget.style.opacity='.88'}
      onMouseLeave={e => e.currentTarget.style.opacity='1'}
    >
      {btnLabel} ↗
    </button>
  </div>
);

const Spinner = () => (
  <div style={{ display: 'flex', justifyContent: 'center', padding: '60px 0' }}>
    <div style={{
      width: 44, height: 44, border: '3px solid #e2e8f0',
      borderTopColor: '#0891b2', borderRadius: '50%',
      animation: 'spin 0.75s linear infinite',
    }} />
    <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
  </div>
);

const EmptyState = ({ text }) => (
  <div style={{ textAlign: 'center', padding: '60px 0', color: '#94a3b8', fontSize: 15 }}>{text}</div>
);

/* ═══════════════════════════════════════════════════════════════════════════
   INLINE QUIZ COMPONENT
═══════════════════════════════════════════════════════════════════════════ */
const InlineQuiz = ({ questions, source, chapterTitle, grade, subjectLabel, onDone, onBack }) => {
  const [idx,      setIdx]      = useState(0);
  const [answers,  setAnswers]  = useState({});   // { questionIdx: chosenOptionIdx }
  const [finished, setFinished] = useState(false);

  const q     = questions[idx];
  const total = questions.length;
  const allAnswered = Object.keys(answers).length === total;

  const choose = (optIdx) => setAnswers(prev => ({ ...prev, [idx]: optIdx }));

  const submit = () => setFinished(true);

  if (!q) return <EmptyState text="No questions available." />;

  /* ── results screen ── */
  if (finished) {
    const correct = questions.filter((_, i) => answers[i] === questions[i].correct).length;
    const pct     = Math.round((correct / total) * 100);
    const passed  = pct >= 50;
    return (
      <div style={{ maxWidth: 640, margin: '0 auto' }}>
        {/* score card */}
        <div style={{
          background: passed
            ? 'linear-gradient(135deg,#16a34a,#15803d)'
            : 'linear-gradient(135deg,#dc2626,#b91c1c)',
          color: '#fff', borderRadius: 18, padding: '32px 28px',
          textAlign: 'center', marginBottom: 24,
          boxShadow: passed ? '0 8px 24px #16a34a44' : '0 8px 24px #dc262644',
        }}>
          <div style={{ fontSize: 52, marginBottom: 8 }}>{passed ? '🎉' : '📚'}</div>
          <div style={{ fontSize: 26, fontWeight: 800, marginBottom: 6 }}>
            {passed ? 'Great Work!' : 'Keep Practising!'}
          </div>
          <div style={{ fontSize: 42, fontWeight: 900, margin: '12px 0' }}>{pct}%</div>
          <div style={{ fontSize: 16, opacity: .9 }}>
            {correct} out of {total} correct
          </div>
          {source === 'fallback' && (
            <div style={{ marginTop: 12, fontSize: 12, opacity: .75, background: 'rgba(255,255,255,.15)', borderRadius: 8, padding: '6px 12px' }}>
              ℹ️ Sample questions used — start Ollama for AI-generated quizzes
            </div>
          )}
        </div>

        {/* per-question review */}
        <p style={{ fontSize: 14, fontWeight: 700, color: '#475569', marginBottom: 12 }}>
          REVIEW
        </p>
        {questions.map((qn, i) => {
          const chosen  = answers[i];
          const isRight = chosen === qn.correct;
          return (
            <div key={i} style={{
              background: '#fff', border: `1.5px solid ${isRight ? '#86efac' : '#fca5a5'}`,
              borderRadius: 12, padding: '16px 18px', marginBottom: 10,
            }}>
              <div style={{ fontSize: 14, fontWeight: 600, color: '#1e293b', marginBottom: 8 }}>
                <span style={{
                  display: 'inline-block', width: 22, height: 22, lineHeight: '22px',
                  borderRadius: '50%', textAlign: 'center', fontSize: 12, fontWeight: 700,
                  background: isRight ? '#16a34a' : '#dc2626', color: '#fff', marginRight: 8,
                }}>{isRight ? '✓' : '✗'}</span>
                {qn.question}
              </div>
              {qn.options.map((opt, oi) => (
                <div key={oi} style={{
                  fontSize: 13, padding: '5px 10px', borderRadius: 6, marginBottom: 3,
                  background: oi === qn.correct ? '#f0fdf4'
                            : oi === chosen     ? '#fef2f2' : 'transparent',
                  color:      oi === qn.correct ? '#16a34a'
                            : oi === chosen     ? '#dc2626' : '#475569',
                  fontWeight: oi === qn.correct ? 700 : 400,
                }}>{opt}</div>
              ))}
              {qn.explanation && (
                <div style={{ fontSize: 12, color: '#64748b', marginTop: 8, fontStyle: 'italic' }}>
                  💡 {qn.explanation}
                </div>
              )}
            </div>
          );
        })}

        <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
          <button onClick={onBack} style={{
            flex: 1, background: '#f1f5f9', color: '#475569', border: 'none',
            borderRadius: 10, padding: '13px 0', fontWeight: 700, fontSize: 15, cursor: 'pointer',
          }}>← Back to Resources</button>
          <button onClick={() => { setIdx(0); setAnswers({}); setFinished(false); }} style={{
            flex: 1, background: 'linear-gradient(135deg,#0891b2,#0e7490)',
            color: '#fff', border: 'none', borderRadius: 10,
            padding: '13px 0', fontWeight: 700, fontSize: 15, cursor: 'pointer',
          }}>🔄 Retry Quiz</button>
        </div>
      </div>
    );
  }

  /* ── question screen ── */
  const progress = ((idx + 1) / total) * 100;

  return (
    <div style={{ maxWidth: 680, margin: '0 auto' }}>
      {/* header */}
      <div style={{
        background: '#fff', borderRadius: 14, padding: '16px 20px',
        marginBottom: 20, display: 'flex', justifyContent: 'space-between',
        alignItems: 'center', boxShadow: '0 1px 4px rgba(0,0,0,.08)',
      }}>
        <div>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#1e293b' }}>{chapterTitle}</div>
          <div style={{ fontSize: 12, color: '#64748b' }}>{subjectLabel} · Grade {grade}</div>
        </div>
        <div style={{ fontSize: 13, fontWeight: 600, color: '#64748b' }}>
          {idx + 1} / {total}
        </div>
      </div>

      {/* progress bar */}
      <div style={{ height: 5, background: '#e2e8f0', borderRadius: 999, marginBottom: 20 }}>
        <div style={{
          height: '100%', background: 'linear-gradient(90deg,#0891b2,#0e7490)',
          borderRadius: 999, width: `${progress}%`, transition: 'width .3s',
        }} />
      </div>

      {/* question */}
      <div style={{
        background: '#fff', borderRadius: 16, padding: '24px 26px',
        marginBottom: 16, boxShadow: '0 1px 6px rgba(0,0,0,.08)',
      }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#0891b2', letterSpacing: '.08em', marginBottom: 10 }}>
          QUESTION {idx + 1}
        </div>
        <div style={{ fontSize: 17, fontWeight: 600, color: '#1e293b', lineHeight: 1.55, marginBottom: 20 }}>
          {q.question}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {(q.options || []).map((opt, oi) => {
            const chosen = answers[idx] === oi;
            return (
              <button key={oi} onClick={() => choose(oi)} style={{
                background: chosen ? '#eff6ff' : '#f8fafc',
                border: `2px solid ${chosen ? '#2563eb' : '#e2e8f0'}`,
                borderRadius: 10, padding: '13px 16px', textAlign: 'left',
                fontSize: 14, color: chosen ? '#1d4ed8' : '#374151',
                fontWeight: chosen ? 600 : 400, cursor: 'pointer',
                transition: 'all .12s',
              }}>
                {opt}
              </button>
            );
          })}
        </div>
      </div>

      {/* nav */}
      <div style={{ display: 'flex', gap: 10 }}>
        <button onClick={() => setIdx(Math.max(0, idx - 1))} disabled={idx === 0} style={{
          flex: 1, background: '#f1f5f9', color: '#475569', border: 'none',
          borderRadius: 10, padding: '13px 0', fontWeight: 600, fontSize: 14,
          cursor: idx === 0 ? 'not-allowed' : 'pointer', opacity: idx === 0 ? .5 : 1,
        }}>← Previous</button>

        {idx < total - 1 ? (
          <button onClick={() => setIdx(idx + 1)} style={{
            flex: 2, background: 'linear-gradient(135deg,#0891b2,#0e7490)',
            color: '#fff', border: 'none', borderRadius: 10,
            padding: '13px 0', fontWeight: 700, fontSize: 14, cursor: 'pointer',
          }}>Next →</button>
        ) : (
          <button onClick={submit} disabled={!allAnswered} style={{
            flex: 2, background: allAnswered
              ? 'linear-gradient(135deg,#16a34a,#15803d)'
              : '#94a3b8',
            color: '#fff', border: 'none', borderRadius: 10,
            padding: '13px 0', fontWeight: 700, fontSize: 14,
            cursor: allAnswered ? 'pointer' : 'not-allowed',
          }}>
            {allAnswered ? '✅ Submit Quiz' : `Answer all ${total} questions`}
          </button>
        )}
      </div>

      {/* dot navigator */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginTop: 16 }}>
        {questions.map((_, i) => (
          <button key={i} onClick={() => setIdx(i)} style={{
            width: 32, height: 32, borderRadius: '50%', border: 'none',
            fontSize: 12, fontWeight: 700, cursor: 'pointer',
            background: i === idx          ? '#0891b2'
                      : answers[i] != null ? '#dcfce7'
                      : '#f1f5f9',
            color:      i === idx          ? '#fff'
                      : answers[i] != null ? '#16a34a'
                      : '#64748b',
          }}>{i + 1}</button>
        ))}
      </div>
    </div>
  );
};
