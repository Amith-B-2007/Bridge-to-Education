import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';
import db from '../../utils/db';

export const ResourceBrowser = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [resources, setResources] = useState([]);
  const [filteredResources, setFilteredResources] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('all');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedGrade, setSelectedGrade] = useState(user?.grade || 5);
  const [selectedResource, setSelectedResource] = useState(null);
  const [loading, setLoading] = useState(true);

  const subjects = ['all', 'Kannada', 'English', 'Maths', 'Science', 'Social Science'];
  const types = ['all', 'pdf', 'video', 'lesson', 'notes'];

  useEffect(() => {
    fetchResources();
  }, [selectedGrade]);

  useEffect(() => {
    filterResources();
  }, [selectedSubject, selectedType, resources]);

  const fetchResources = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/resources/resources/?grade=${selectedGrade}`);
      const data = response.data.results || response.data;
      setResources(data);
      // Cache resources for offline use
      if (Array.isArray(data)) {
        await db.saveResources(data);
      }
    } catch (error) {
      console.error('Error fetching resources:', error);
      // Fallback to cached resources
      try {
        const cached = await db.getAll('resources');
        setResources(cached.filter(r => r.grade === selectedGrade));
      } catch (e) {
        setResources([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const filterResources = () => {
    let filtered = resources;
    if (selectedSubject !== 'all') {
      filtered = filtered.filter(r => r.subject === selectedSubject);
    }
    if (selectedType !== 'all') {
      filtered = filtered.filter(r => r.resource_type === selectedType);
    }
    setFilteredResources(filtered);
  };

  const downloadResource = async (resource) => {
    try {
      await api.post(`/resources/resources/${resource.id}/download/`);
      if (resource.file_url) {
        window.open(resource.file_url, '_blank');
      }
    } catch (error) {
      console.error('Error downloading resource:', error);
    }
  };

  const getResourceIcon = (type) => {
    const icons = {
      pdf: '📄',
      video: '🎥',
      lesson: '📚',
      notes: '📝',
    };
    return icons[type] || '📎';
  };

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
              <h1 className="prof-page-title">📚 Learning Resources</h1>
              <p className="prof-page-subtitle">Browse curated materials by grade, subject, and type</p>
            </div>
          </div>
        </div>
      </header>

      <main className="prof-main">
        <div className="prof-surface p-6 mb-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Filter Resources</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Grade</label>
              <select
                value={selectedGrade}
                onChange={(e) => setSelectedGrade(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-100 focus:border-cyan-500"
              >
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(g => (
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
                {subjects.map(s => (
                  <option key={s} value={s}>{s === 'all' ? 'All Subjects' : s}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-100 focus:border-cyan-500"
              >
                {types.map(t => (
                  <option key={t} value={t}>{t === 'all' ? 'All Types' : t.toUpperCase()}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : filteredResources.length === 0 ? (
          <div className="prof-surface p-12 text-center">
            <p className="text-gray-500 text-lg">No resources found for these filters.</p>
            <p className="text-gray-400 text-sm mt-2">Try changing the grade or subject filter.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredResources.map((resource) => (
              <div
                key={resource.id}
                className="prof-surface hover:shadow-xl transition-shadow cursor-pointer"
                onClick={() => setSelectedResource(resource)}
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-3">
                    <span className="text-4xl">{getResourceIcon(resource.resource_type)}</span>
                    <span className="text-xs bg-cyan-100 text-cyan-800 px-2 py-1 rounded-full">
                      {resource.resource_type?.toUpperCase()}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2">
                    {resource.title}
                  </h3>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {resource.description}
                  </p>
                  <div className="flex justify-between items-center text-xs text-gray-500">
                    <span>{resource.subject}</span>
                    <span>Grade {resource.grade}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {selectedResource && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
             onClick={() => setSelectedResource(null)}>
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto border border-slate-200"
               onClick={e => e.stopPropagation()}>
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-900">{selectedResource.title}</h2>
                <button
                  onClick={() => setSelectedResource(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>
              <div className="space-y-3 mb-6">
                <p><span className="font-semibold">Subject:</span> {selectedResource.subject}</p>
                <p><span className="font-semibold">Grade:</span> {selectedResource.grade}</p>
                <p><span className="font-semibold">Type:</span> {selectedResource.resource_type?.toUpperCase()}</p>
                <p className="text-gray-700">{selectedResource.description}</p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => downloadResource(selectedResource)}
                  className="flex-1 bg-cyan-600 text-white px-4 py-2 rounded-lg hover:bg-cyan-700"
                >
                  Open / Download
                </button>
                <button
                  onClick={() => setSelectedResource(null)}
                  className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
