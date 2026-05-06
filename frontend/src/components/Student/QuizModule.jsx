import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';

export const QuizModule = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [quizzes, setQuizzes] = useState([]);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSubject, setSelectedSubject] = useState('all');
  const [selectedGrade, setSelectedGrade] = useState(user?.grade || 5);

  const subjects = ['all', 'Kannada', 'English', 'Maths', 'Science', 'Social Science'];

  useEffect(() => {
    fetchQuizzes();
  }, [selectedGrade]);

  const fetchQuizzes = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/quizzes/?grade=${selectedGrade}`);
      setQuizzes(response.data.results || response.data || []);
    } catch (error) {
      console.error('Error fetching quizzes:', error);
      setQuizzes([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredQuizzes = selectedSubject === 'all'
    ? quizzes
    : quizzes.filter(q => q.subject === selectedSubject);

  if (selectedQuiz) {
    return <QuizTaker quiz={selectedQuiz} onComplete={() => { setSelectedQuiz(null); fetchQuizzes(); }} onBack={() => setSelectedQuiz(null)} />;
  }

  return (
    <div className="prof-page-shell">
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
              <h1 className="prof-page-title">📝 Quizzes</h1>
              <p className="prof-page-subtitle">Take chapter-wise assessments and track outcomes</p>
            </div>
          </div>
        </div>
      </header>

      <main className="prof-main">
        <div className="prof-surface p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Grade</label>
              <select
                value={selectedGrade}
                onChange={(e) => setSelectedGrade(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-100 focus:border-cyan-500"
              >
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((g) => (
                  <option key={g} value={g}>Grade {g}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
              <select
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-100 focus:border-cyan-500"
              >
                {subjects.map((s) => (
                  <option key={s} value={s}>{s === 'all' ? 'All Subjects' : s}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600"></div>
          </div>
        ) : filteredQuizzes.length === 0 ? (
          <div className="prof-surface p-12 text-center">
            <p className="text-gray-500 text-lg">No quizzes available for these filters.</p>
            <p className="text-gray-400 text-sm mt-2">Try changing the grade or subject filter.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredQuizzes.map((quiz) => (
              <div key={quiz.id} className="prof-surface hover:shadow-xl transition-shadow">
                <div className="p-6">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="text-lg font-bold text-gray-900">{quiz.title}</h3>
                    <span className="text-xs bg-cyan-100 text-cyan-800 px-2 py-1 rounded-full">
                      {quiz.subject}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {quiz.description || 'No description'}
                  </p>
                  <div className="grid grid-cols-2 gap-2 text-sm text-gray-700 mb-4">
                    <div>📚 Grade {quiz.grade}</div>
                    <div>❓ {quiz.num_questions || 0} Questions</div>
                    <div>⏱️ {quiz.duration_minutes || 30} mins</div>
                    <div>🎯 {quiz.total_marks || 0} Marks</div>
                  </div>
                  <button
                    onClick={() => setSelectedQuiz(quiz)}
                    className="w-full bg-cyan-600 text-white py-2 rounded-lg hover:bg-cyan-700"
                  >
                    Start Quiz
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
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

  useEffect(() => {
    fetchQuiz();
  }, []);

  const fetchQuiz = async () => {
    try {
      const response = await api.get(`/quizzes/${quiz.id}/`);
      setQuestions(response.data.questions || []);
    } catch (error) {
      console.error('Error fetching quiz details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = (questionId, answer) => {
    setAnswers({ ...answers, [questionId]: answer });
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const response = await api.post(`/quizzes/${quiz.id}/submit/`, {
        answers_json: answers,
      });
      setResult(response.data);
    } catch (error) {
      console.error('Error submitting quiz:', error);
      alert('Failed to submit quiz. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (result) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-8 text-center">
          <div className="text-6xl mb-4">{result.passed ? '🎉' : '📚'}</div>
          <h2 className="text-3xl font-bold mb-4">
            {result.passed ? 'Congratulations!' : 'Keep Learning!'}
          </h2>
          <div className="space-y-2 mb-6">
            <p className="text-2xl font-bold text-blue-600">
              {result.score} / {result.total_marks}
            </p>
            <p className="text-xl text-gray-600">
              {Math.round(result.percentage)}%
            </p>
          </div>
          <p className="text-gray-700 mb-6">{result.feedback}</p>
          <button
            onClick={onComplete}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-medium"
          >
            Back to Quizzes
          </button>
        </div>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-700 mb-4">No questions available for this quiz.</p>
          <button onClick={onBack} className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg">
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentIndex];
  const progress = ((currentIndex + 1) / questions.length) * 100;
  const allAnswered = questions.every(q => answers[q.id] !== undefined);

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-slate-900">{quiz.title}</h1>
          <span className="text-sm text-gray-600">
            Question {currentIndex + 1} of {questions.length}
          </span>
        </div>
        <div className="w-full bg-gray-200 h-1">
          <div className="bg-cyan-600 h-1 transition-all" style={{ width: `${progress}%` }}></div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8">
          <h2 className="text-xl font-bold mb-6">{currentQuestion.question_text}</h2>
          <div className="space-y-3">
            {(currentQuestion.options || []).map((opt, idx) => {
              const optKey = typeof opt === 'string' ? opt : opt.key || `option_${idx}`;
              const optText = typeof opt === 'string' ? opt : opt.text || opt;
              const isSelected = answers[currentQuestion.id] === optKey;
              return (
                <button
                  key={idx}
                  onClick={() => handleAnswer(currentQuestion.id, optKey)}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                    isSelected
                      ? 'border-cyan-600 bg-cyan-50'
                      : 'border-gray-200 hover:border-gray-400'
                  }`}
                >
                  <span className="font-medium mr-2">{String.fromCharCode(65 + idx)}.</span>
                  {optText}
                </button>
              );
            })}
          </div>

          <div className="flex justify-between mt-8">
            <button
              onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))}
              disabled={currentIndex === 0}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg disabled:opacity-50 hover:bg-gray-300"
            >
              ← Previous
            </button>
            {currentIndex < questions.length - 1 ? (
              <button
                onClick={() => setCurrentIndex(currentIndex + 1)}
                className="px-6 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700"
              >
                Next →
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={!allAnswered || submitting}
                className="px-6 py-2 bg-green-600 text-white rounded-lg disabled:opacity-50 hover:bg-green-700"
              >
                {submitting ? 'Submitting...' : 'Submit Quiz'}
              </button>
            )}
          </div>
        </div>

        <div className="mt-6 flex flex-wrap gap-2 justify-center">
          {questions.map((q, idx) => (
            <button
              key={q.id}
              onClick={() => setCurrentIndex(idx)}
              className={`w-10 h-10 rounded-full text-sm font-medium ${
                idx === currentIndex
                  ? 'bg-cyan-600 text-white'
                  : answers[q.id] !== undefined
                  ? 'bg-green-100 text-green-800 border border-green-400'
                  : 'bg-white text-gray-700 border border-gray-300'
              }`}
            >
              {idx + 1}
            </button>
          ))}
        </div>
      </main>
    </div>
  );
};
