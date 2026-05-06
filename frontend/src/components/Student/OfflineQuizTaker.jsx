import { useState, useEffect } from 'react';
import db from '../../utils/db';
import { offlineManager } from '../../utils/offline';

export function OfflineQuizTaker({ quizId, onComplete }) {
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadQuiz = async () => {
      try {
        const cached = await db.get('quizzes', quizId);
        if (cached) {
          setQuiz(cached);
          const initAnswers = {};
          (cached.questions || []).forEach((q, idx) => {
            initAnswers[idx] = null;
          });
          setAnswers(initAnswers);
        }
      } finally {
        setLoading(false);
      }
    };

    loadQuiz();
  }, [quizId]);

  const handleSelectAnswer = (questionIndex, selectedOption) => {
    setAnswers(prev => ({
      ...prev,
      [questionIndex]: selectedOption
    }));
  };

  const handleSubmit = async () => {
    if (!quiz) return;

    const attempt = {
      id: `attempt_${Date.now()}`,
      quiz_id: quizId,
      answers: answers,
      submitted_at: new Date().toISOString(),
      is_synced: false
    };

    try {
      await db.put('quiz_attempts', attempt);
      await db.savePendingAction({
        type: 'quiz_submit',
        endpoint: `/quizzes/${quizId}/submit/`,
        payload: {
          answers: answers,
          submitted_at: attempt.submitted_at
        }
      });

      alert('Quiz submitted! It will sync when you go online.');

      if (offlineManager.isOnline) {
        offlineManager.syncPendingActions();
      }

      onComplete?.(attempt);
    } catch (error) {
      console.error('Failed to save quiz:', error);
      alert('Error saving quiz. Please try again.');
    }
  };

  if (loading) {
    return <div className="text-center p-4">Loading quiz...</div>;
  }

  if (!quiz) {
    return <div className="text-center p-4 text-red-600">Quiz not found offline</div>;
  }

  const questions = quiz.questions || [];
  const question = questions[currentQuestion];

  return (
    <div className="max-w-2xl mx-auto p-4">
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <h1 className="text-2xl font-bold">{quiz.title}</h1>
          <span className="text-sm text-gray-600">
            Question {currentQuestion + 1} of {questions.length}
          </span>
        </div>
        <div className="w-full bg-gray-200 h-2 rounded">
          <div
            className="bg-cyan-600 h-2 rounded transition-all"
            style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
          />
        </div>
      </div>

      {question && (
        <div className="bg-white border border-slate-200 rounded-xl p-6 mb-4 shadow-sm">
          <h2 className="text-lg font-semibold mb-4">{question.question_text}</h2>

          <div className="space-y-2">
            {(question.options || []).map((option, idx) => (
              <label key={idx} className="flex items-center p-3 border border-slate-200 rounded hover:bg-cyan-50 cursor-pointer">
                <input
                  type="radio"
                  name={`question_${currentQuestion}`}
                  checked={answers[currentQuestion] === option}
                  onChange={() => handleSelectAnswer(currentQuestion, option)}
                  className="mr-3"
                />
                <span>{option}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      <div className="flex justify-between gap-4">
        <button
          onClick={() => setCurrentQuestion(prev => Math.max(0, prev - 1))}
          disabled={currentQuestion === 0}
          className="px-4 py-2 bg-gray-300 rounded disabled:opacity-50 hover:bg-gray-400"
        >
          Previous
        </button>

        {currentQuestion < questions.length - 1 ? (
          <button
            onClick={() => setCurrentQuestion(prev => prev + 1)}
            className="px-4 py-2 bg-cyan-600 text-white rounded hover:bg-cyan-700"
          >
            Next
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            Submit Quiz
          </button>
        )}
      </div>
    </div>
  );
}
