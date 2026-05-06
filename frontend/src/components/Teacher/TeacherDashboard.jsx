import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';

export const TeacherDashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [doubts, setDoubts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPendingDoubts();
  }, []);

  const fetchPendingDoubts = async () => {
    try {
      const response = await api.get('/doubts/sessions/?status=open');
      setDoubts(response.data.results || response.data || []);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prof-page-shell">
      <header className="prof-page-header">
        <div className="prof-page-header-inner">
          <div>
            <h1 className="prof-page-title">👨‍🏫 Teacher Portal</h1>
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

      <nav className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-1">
            {[
              { id: 'overview', label: '📊 Overview' },
              { id: 'doubts', label: '💬 Doubts' },
              { id: 'upload', label: '📤 Upload Resources' },
              { id: 'marks', label: '📝 Upload Marks' },
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
        {activeTab === 'overview' && <Overview doubts={doubts} />}
        {activeTab === 'doubts' && <DoubtsPanel doubts={doubts} loading={loading} onRefresh={fetchPendingDoubts} />}
        {activeTab === 'upload' && <ResourceUpload />}
        {activeTab === 'marks' && <MarksUpload />}
      </main>
    </div>
  );
};

const Overview = ({ doubts }) => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
    <div className="prof-surface p-6">
      <p className="text-gray-600 text-sm">Pending Doubts</p>
      <p className="text-4xl font-bold mt-2 text-cyan-700">{doubts.length}</p>
    </div>
    <div className="prof-surface p-6">
      <p className="text-gray-600 text-sm">Resources Uploaded</p>
      <p className="text-4xl font-bold mt-2 text-cyan-700">--</p>
    </div>
    <div className="prof-surface p-6">
      <p className="text-gray-600 text-sm">Active Students</p>
      <p className="text-4xl font-bold mt-2 text-cyan-700">--</p>
    </div>
  </div>
);

const DoubtsPanel = ({ doubts, loading, onRefresh }) => {
  const [activeDoubt, setActiveDoubt] = useState(null);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="prof-surface">
      <div className="p-6 border-b border-slate-200 flex justify-between items-center">
        <h2 className="text-xl font-bold">Student Doubts</h2>
        <button onClick={onRefresh} className="text-cyan-700 hover:text-cyan-800 text-sm font-semibold">
          🔄 Refresh
        </button>
      </div>
      {doubts.length === 0 ? (
        <div className="p-12 text-center text-gray-500">
          No pending doubts at the moment.
        </div>
      ) : (
        <div className="divide-y">
          {doubts.map(doubt => (
            <div key={doubt.id} className="p-6 hover:bg-gray-50">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="font-bold">{doubt.subject}</h3>
                  <p className="text-sm text-gray-600 mt-1">{doubt.description}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs ${
                  doubt.status === 'open' ? 'bg-yellow-100 text-yellow-800' :
                  doubt.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {doubt.status}
                </span>
              </div>
              <div className="flex gap-2 mt-3">
                <button className="bg-cyan-600 text-white px-4 py-1 rounded text-sm hover:bg-cyan-700">
                  Reply
                </button>
                <button className="bg-green-600 text-white px-4 py-1 rounded text-sm hover:bg-green-700">
                  Mark Resolved
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const ResourceUpload = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    grade: 5,
    subject: 'Maths',
    chapter: '',
    resource_type: 'pdf',
  });
  const [file, setFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage('');

    try {
      const data = new FormData();
      Object.entries(formData).forEach(([key, value]) => data.append(key, value));
      if (file) data.append('file', file);

      await api.post('/resources/resources/', data, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setMessage('✅ Resource uploaded successfully!');
      setFormData({ title: '', description: '', grade: 5, subject: 'Maths', chapter: '', resource_type: 'pdf' });
      setFile(null);
    } catch (error) {
      setMessage('❌ Upload failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="prof-surface p-6 max-w-3xl mx-auto">
      <h2 className="text-xl font-bold mb-6">Upload Learning Resource</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Title</label>
          <input
            type="text"
            required
            value={formData.title}
            onChange={e => setFormData({...formData, title: e.target.value})}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-100 focus:border-cyan-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Description</label>
          <textarea
            value={formData.description}
            onChange={e => setFormData({...formData, description: e.target.value})}
            rows="3"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-100 focus:border-cyan-500"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Grade</label>
            <select
              value={formData.grade}
              onChange={e => setFormData({...formData, grade: Number(e.target.value)})}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-100 focus:border-cyan-500"
            >
              {[1,2,3,4,5,6,7,8,9,10].map(g => <option key={g} value={g}>Grade {g}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Subject</label>
            <select
              value={formData.subject}
              onChange={e => setFormData({...formData, subject: e.target.value})}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-100 focus:border-cyan-500"
            >
              {['Kannada', 'English', 'Maths', 'Science', 'Social Science'].map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Chapter</label>
            <input
              type="text"
              value={formData.chapter}
              onChange={e => setFormData({...formData, chapter: e.target.value})}
              placeholder="e.g., Chapter 1"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-100 focus:border-cyan-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Type</label>
            <select
              value={formData.resource_type}
              onChange={e => setFormData({...formData, resource_type: e.target.value})}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-100 focus:border-cyan-500"
            >
              <option value="pdf">PDF</option>
              <option value="video">Video</option>
              <option value="lesson">Lesson</option>
              <option value="notes">Notes</option>
            </select>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">File</label>
          <input
            type="file"
            onChange={e => setFile(e.target.files[0])}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-100 focus:border-cyan-500"
          />
        </div>
        {message && (
          <div className={`p-3 rounded-lg ${message.includes('✅') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {message}
          </div>
        )}
        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-cyan-600 text-white py-2 rounded-lg hover:bg-cyan-700 disabled:opacity-50"
        >
          {submitting ? 'Uploading...' : 'Upload Resource'}
        </button>
      </form>
    </div>
  );
};

const MarksUpload = () => {
  const [grade, setGrade] = useState(5);
  const [subject, setSubject] = useState('Maths');
  const [marks, setMarks] = useState([{ student_id: '', marks: '' }]);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const addRow = () => setMarks([...marks, { student_id: '', marks: '' }]);
  const updateRow = (idx, field, value) => {
    const newMarks = [...marks];
    newMarks[idx][field] = value;
    setMarks(newMarks);
  };
  const removeRow = (idx) => setMarks(marks.filter((_, i) => i !== idx));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage('');
    try {
      await api.post('/notifications/marks-upload/', {
        grade,
        subject,
        marks_data: marks.filter(m => m.student_id && m.marks),
      });
      setMessage('✅ Marks uploaded and SMS notifications sent!');
      setMarks([{ student_id: '', marks: '' }]);
    } catch (error) {
      setMessage('❌ Failed to upload marks: ' + (error.response?.data?.detail || error.message));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="prof-surface p-6 max-w-3xl mx-auto">
      <h2 className="text-xl font-bold mb-6">Upload Student Marks</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Grade</label>
            <select value={grade} onChange={e => setGrade(Number(e.target.value))} className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-100 focus:border-cyan-500">
              {[1,2,3,4,5,6,7,8,9,10].map(g => <option key={g} value={g}>Grade {g}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Subject</label>
            <select value={subject} onChange={e => setSubject(e.target.value)} className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-100 focus:border-cyan-500">
              {['Kannada', 'English', 'Maths', 'Science', 'Social Science'].map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        </div>
        <div>
          <h3 className="font-medium mb-2">Student Marks</h3>
          {marks.map((m, idx) => (
            <div key={idx} className="grid grid-cols-12 gap-2 mb-2">
              <input
                placeholder="Student ID"
                value={m.student_id}
                onChange={e => updateRow(idx, 'student_id', e.target.value)}
                className="col-span-6 px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-100 focus:border-cyan-500"
              />
              <input
                type="number"
                placeholder="Marks"
                value={m.marks}
                onChange={e => updateRow(idx, 'marks', e.target.value)}
                className="col-span-4 px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-100 focus:border-cyan-500"
              />
              <button
                type="button"
                onClick={() => removeRow(idx)}
                className="col-span-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
              >
                Remove
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={addRow}
            className="text-cyan-700 hover:text-cyan-800 text-sm font-semibold"
          >
            + Add Another Student
          </button>
        </div>
        {message && (
          <div className={`p-3 rounded-lg ${message.includes('✅') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {message}
          </div>
        )}
        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
        >
          {submitting ? 'Uploading...' : 'Upload Marks & Send SMS'}
        </button>
      </form>
    </div>
  );
};
