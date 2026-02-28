import { useEffect, useState } from 'react';
import { careersApi, pathsApi } from '../services/api';
import type { Career, PathTemplate } from '../types';
import { Plus, BookOpen, ExternalLink, Save, X } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import ActionMenu from '../components/ActionMenu';

export default function PathCreationPage() {
  const [careers, setCareers] = useState<Career[]>([]);
  const [paths, setPaths] = useState<PathTemplate[]>([]);
  const [selectedCareer, setSelectedCareer] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Form state
  const [showNewPathForm, setShowNewPathForm] = useState(false);
  const [newPath, setNewPath] = useState({
    name: '',
    description: '',
    careerId: 0,
    durationHours: 0,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [careersRes, pathsRes] = await Promise.all([
        careersApi.list(1, 100),
        pathsApi.list(1, 100),
      ]);
      setCareers(careersRes.items);
      setPaths(pathsRes.items);
      if (careersRes.items.length > 0) {
        setSelectedCareer(careersRes.items[0].careerId);
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreatePath = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await pathsApi.create(newPath);
      setShowNewPathForm(false);
      setNewPath({ name: '', description: '', careerId: 0, durationHours: 0 });
      fetchData();
    } catch (error) {
      console.error('Failed to create path:', error);
    }
  };

  const filteredPaths = selectedCareer
    ? paths.filter((p) => p.careerId === selectedCareer)
    : paths;

  const seniorityLevels = ['Junior', 'Semi Senior', 'Senior', 'Lead'];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Path Creation</h1>
        <p className="mt-1 text-gray-500">
          Manage career path structure: add, edit, or remove paths for different career types
        </p>
      </div>

      {/* New path form modal */}
      {showNewPathForm && (
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Create New Path</h2>
            <button
              onClick={() => setShowNewPathForm(false)}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <form onSubmit={handleCreatePath} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Path Name
                </label>
                <input
                  type="text"
                  value={newPath.name}
                  onChange={(e) => setNewPath({ ...newPath, name: e.target.value })}
                  className="input"
                  placeholder="e.g., React Fundamentals"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Career Track
                </label>
                <select
                  value={newPath.careerId}
                  onChange={(e) => setNewPath({ ...newPath, careerId: parseInt(e.target.value) })}
                  className="select"
                  required
                >
                  <option value={0}>Select a career...</option>
                  {careers.map((career) => (
                    <option key={career.careerId} value={career.careerId}>
                      {career.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
              <textarea
                value={newPath.description}
                onChange={(e) => setNewPath({ ...newPath, description: e.target.value })}
                className="input min-h-[80px] resize-none"
                placeholder="Describe what learners will achieve..."
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duration (hours)
              </label>
              <input
                type="number"
                value={newPath.durationHours || ''}
                onChange={(e) =>
                  setNewPath({ ...newPath, durationHours: parseInt(e.target.value) || 0 })
                }
                className="input w-32"
                min="1"
                required
              />
            </div>

            <div className="flex items-center gap-3 pt-4 border-t border-gray-200">
              <button type="submit" className="btn btn-primary flex items-center gap-2">
                <Save className="w-4 h-4" />
                Create Path
              </button>
              <button
                type="button"
                onClick={() => setShowNewPathForm(false)}
                className="btn btn-ghost"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Main content card */}
      <div className="card">
        {/* Filter and Add button */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <span className="text-gray-600 text-sm">Filter by Career:</span>
            <select
              value={selectedCareer || ''}
              onChange={(e) => setSelectedCareer(e.target.value ? parseInt(e.target.value) : null)}
              className="select w-auto"
            >
              {careers.map((career) => (
                <option key={career.careerId} value={career.careerId}>
                  {career.name}
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={() => setShowNewPathForm(true)}
            className="btn btn-outline flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add Path
          </button>
        </div>

        {/* Paths table */}
        {filteredPaths.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center mx-auto mb-4">
              <BookOpen className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No paths created yet</h3>
            <p className="text-gray-500 mb-6">
              Create your first learning path template to get started.
            </p>
            <button
              onClick={() => setShowNewPathForm(true)}
              className="btn btn-primary inline-flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Create Path
            </button>
          </div>
        ) : (
          <div className="overflow-visible">
            <table className="table">
              <thead>
                <tr>
                  <th>Seniority</th>
                  <th>Path Name</th>
                  <th>Description</th>
                  <th>Start Date</th>
                  <th>Deadline</th>
                  <th>Duration</th>
                  <th>Link</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredPaths.map((path, index) => (
                  <tr key={path.pathTemplateId}>
                    <td className="text-gray-600">
                      {seniorityLevels[index % seniorityLevels.length]}
                    </td>
                    <td>
                      <span className="font-semibold text-gray-900">{path.name}</span>
                    </td>
                    <td className="text-gray-500 max-w-xs truncate">
                      {path.description}
                    </td>
                    <td className="text-gray-600">
                      {new Date().toLocaleDateString()}
                    </td>
                    <td className="text-gray-600">
                      {new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toLocaleDateString()}
                    </td>
                    <td className="text-gray-600">{path.durationHours} hours</td>
                    <td>
                      <a href="#" className="text-primary-500 hover:text-primary-600 flex items-center gap-1">
                        Open Link
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </td>
                    <td>
                      <ActionMenu
                        items={[
                          {
                            label: 'Edit Path',
                            onClick: () => console.log('Edit', path.pathTemplateId),
                          },
                          {
                            label: 'View Steps',
                            onClick: () => console.log('View Steps', path.pathTemplateId),
                          },
                          {
                            label: 'Delete',
                            onClick: () => console.log('Delete', path.pathTemplateId),
                            danger: true,
                          },
                        ]}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
