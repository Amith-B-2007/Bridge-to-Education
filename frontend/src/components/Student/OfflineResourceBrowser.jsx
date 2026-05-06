import { useState, useEffect } from 'react';
import db from '../../utils/db';

function ResourceModal({ resource, onClose }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl border border-slate-200 p-6 max-w-lg w-full shadow-xl">
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-xl font-bold">{resource.title}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <p className="text-gray-700 mb-4">{resource.description}</p>

        <div className="bg-slate-50 border border-slate-200 p-3 rounded mb-4 text-sm space-y-1">
          <p><strong>Type:</strong> {resource.resource_type}</p>
          <p><strong>Chapter:</strong> {resource.chapter}</p>
          <p><strong>Size:</strong> {(resource.file_size / 1024 / 1024).toFixed(2)} MB</p>
          <p><strong>Status:</strong> <span className="text-green-600">✓ Cached</span></p>
        </div>

        <button
          className="w-full bg-cyan-600 text-white py-2 rounded hover:bg-cyan-700"
          onClick={() => {
            window.open(resource.file_path, '_blank');
            onClose();
          }}
        >
          Open Resource
        </button>
      </div>
    </div>
  );
}

export function OfflineResourceBrowser({ grade, subject }) {
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedResource, setSelectedResource] = useState(null);

  useEffect(() => {
    const loadResources = async () => {
      try {
        const cached = await db.getResourcesByGradeSubject(grade, subject);
        setResources(cached);
      } catch (error) {
        console.error('Failed to load offline resources:', error);
      } finally {
        setLoading(false);
      }
    };

    loadResources();
  }, [grade, subject]);

  if (loading) {
    return <div className="text-center p-4">Loading cached resources...</div>;
  }

  if (resources.length === 0) {
    return (
      <div className="text-center p-4 text-gray-500">
        <p>No resources cached for {subject} (Grade {grade})</p>
        <p className="text-sm mt-2">Download resources while online to use offline</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4">
      {resources.map(resource => (
        <div
          key={resource.id}
          className="bg-white border border-slate-200 rounded-xl p-4 cursor-pointer hover:shadow-lg transition"
          onClick={() => setSelectedResource(resource)}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="font-semibold text-gray-800">{resource.title}</h3>
              <p className="text-sm text-gray-600 mt-1">{resource.description}</p>
              <div className="flex gap-2 mt-3">
                <span className="inline-block px-2 py-1 bg-cyan-100 text-cyan-800 text-xs rounded">
                  {resource.resource_type}
                </span>
                <span className="inline-block px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded">
                  {(resource.file_size / 1024 / 1024).toFixed(2)} MB
                </span>
              </div>
            </div>
            <div className="text-green-600 text-lg">✓</div>
          </div>
        </div>
      ))}

      {selectedResource && (
        <ResourceModal
          resource={selectedResource}
          onClose={() => setSelectedResource(null)}
        />
      )}
    </div>
  );
}
