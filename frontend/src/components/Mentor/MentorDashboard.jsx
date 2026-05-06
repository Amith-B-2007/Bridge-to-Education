import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';

export const MentorDashboard = () => {
  const { user, logout } = useAuth();
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = async () => {
    try {
      const response = await api.get('/users/students/');
      setStudents(response.data.results || response.data || []);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStudentProgress = async (studentId) => {
    try {
      const response = await api.get(`/users/students/${studentId}/progress/`);
      setProgress(response.data);
    } catch (error) {
      console.error('Error:', error);
      setProgress(null);
    }
  };

  const selectStudent = (student) => {
    setSelectedStudent(student);
    fetchStudentProgress(student.id);
  };

  return (
    <div className="prof-page-shell">
      <header className="prof-page-header">
        <div className="prof-page-header-inner">
          <div>
            <h1 className="prof-page-title">🧑‍🏫 Mentor Portal</h1>
            <p className="prof-page-subtitle">Welcome, {user?.username}</p>
          </div>
          <button
            onClick={logout}
            className="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg border border-white/20"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="prof-main">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="prof-surface">
            <div className="p-4 border-b border-slate-200">
              <h2 className="font-bold">My Students ({students.length})</h2>
            </div>
            <div className="max-h-[70vh] overflow-y-auto">
              {loading ? (
                <div className="p-4 text-gray-500">Loading...</div>
              ) : students.length === 0 ? (
                <div className="p-4 text-gray-500">No students assigned</div>
              ) : (
                students.map(student => (
                  <button
                    key={student.id}
                    onClick={() => selectStudent(student)}
                    className={`w-full text-left p-4 border-b border-slate-100 hover:bg-slate-50 ${
                      selectedStudent?.id === student.id ? 'bg-cyan-50 border-l-4 border-l-cyan-600' : ''
                    }`}
                  >
                    <div className="font-medium">{student.user?.first_name || student.user?.username}</div>
                    <div className="text-sm text-gray-500">Grade {student.grade}</div>
                  </button>
                ))
              )}
            </div>
          </div>

          <div className="md:col-span-2">
            {selectedStudent ? (
              <StudentProgress student={selectedStudent} progress={progress} />
            ) : (
                <div className="prof-surface p-12 text-center">
                <p className="text-gray-500 text-lg">Select a student to view their progress</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

const StudentProgress = ({ student, progress }) => {
  const subjects = ['Kannada', 'English', 'Maths', 'Science', 'Social Science'];

  return (
    <div className="space-y-6">
      <div className="prof-surface p-6">
        <h2 className="text-2xl font-bold mb-4">
          {student.user?.first_name || student.user?.username}'s Progress
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-cyan-50 rounded-lg p-4">
            <p className="text-sm text-cyan-700">Grade</p>
            <p className="text-2xl font-bold">{student.grade}</p>
          </div>
          <div className="bg-cyan-50 rounded-lg p-4">
            <p className="text-sm text-cyan-700">Quiz Attempts</p>
            <p className="text-2xl font-bold">{student.total_quiz_attempts || 0}</p>
          </div>
          <div className="bg-cyan-50 rounded-lg p-4">
            <p className="text-sm text-cyan-700">Sessions</p>
            <p className="text-2xl font-bold">{student.total_sessions || 0}</p>
          </div>
          <div className="bg-cyan-50 rounded-lg p-4">
            <p className="text-sm text-cyan-700">Avg Score</p>
            <p className="text-2xl font-bold">{progress?.avg_score || 0}%</p>
          </div>
        </div>
      </div>

      <div className="prof-surface p-6">
        <h3 className="font-bold mb-4">Subject Progress</h3>
        <div className="space-y-3">
          {subjects.map(subject => {
            const data = progress?.subjects?.[subject] || { avg_score: 0, chapters_completed: 0 };
            return (
              <div key={subject}>
                <div className="flex justify-between mb-1">
                  <span className="font-medium">{subject}</span>
                  <span className="text-sm text-gray-600">{data.avg_score || 0}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-cyan-600 h-3 rounded-full transition-all"
                    style={{ width: `${data.avg_score || 0}%` }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="prof-surface p-6">
        <h3 className="font-bold mb-4">💡 Guidance Suggestions</h3>
        <ul className="space-y-2 text-gray-700">
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span>Encourage daily AI Tutor sessions for weaker subjects</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span>Review recent quiz attempts and discuss mistakes</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span>Schedule weekly check-in calls with parents</span>
          </li>
        </ul>
      </div>
    </div>
  );
};
