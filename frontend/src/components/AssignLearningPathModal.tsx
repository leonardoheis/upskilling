import { useState, useEffect } from 'react';
import { X, Calendar, BookOpen } from 'lucide-react';
import { pathsApi, progressApi } from '../services/api';
import type { PathTemplate, UserCareerPathDetail } from '../types';
import LoadingSpinner from './LoadingSpinner';

interface AssignLearningPathModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  careerPath: UserCareerPathDetail | null;
}

export default function AssignLearningPathModal({
  isOpen,
  onClose,
  onSuccess,
  careerPath,
}: AssignLearningPathModalProps) {
  const [pathTemplates, setPathTemplates] = useState<PathTemplate[]>([]);
  const [selectedPathId, setSelectedPathId] = useState<number | ''>('');
  const [startDate, setStartDate] = useState('');
  const [deadline, setDeadline] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Fetch path templates for the career
  useEffect(() => {
    if (isOpen && careerPath) {
      const fetchPaths = async () => {
        setIsLoading(true);
        try {
          const response = await pathsApi.list(1, 100, careerPath.careerId);
          // Filter out already assigned paths
          const assignedPathIds = careerPath.pathAssignments.map((a) => a.pathTemplateId);
          const availablePaths = response.items.filter(
            (p) => !assignedPathIds.includes(p.pathTemplateId)
          );
          setPathTemplates(availablePaths);
        } catch (err) {
          console.error('Failed to fetch paths:', err);
          setError('Failed to load learning paths');
        } finally {
          setIsLoading(false);
        }
      };
      fetchPaths();

      // Set default dates based on career path dates
      const today = new Date();
      const careerEndDate = new Date(careerPath.endDate);
      const defaultStart = today > new Date(careerPath.startDate) ? today : new Date(careerPath.startDate);
      const defaultDeadline = new Date(defaultStart);
      defaultDeadline.setMonth(defaultDeadline.getMonth() + 1);
      
      // Don't exceed career end date
      const finalDeadline = defaultDeadline < careerEndDate ? defaultDeadline : careerEndDate;

      setStartDate(defaultStart.toISOString().split('T')[0]);
      setDeadline(finalDeadline.toISOString().split('T')[0]);
    }
  }, [isOpen, careerPath]);

  // Auto-set dates when path is selected based on duration
  useEffect(() => {
    if (selectedPathId && startDate) {
      const selectedPath = pathTemplates.find((p) => p.pathTemplateId === selectedPathId);
      if (selectedPath?.defaultDeadlineOffsetDays) {
        const start = new Date(startDate);
        const newDeadline = new Date(start);
        newDeadline.setDate(newDeadline.getDate() + selectedPath.defaultDeadlineOffsetDays);
        setDeadline(newDeadline.toISOString().split('T')[0]);
      }
    }
  }, [selectedPathId, startDate, pathTemplates]);

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setSelectedPathId('');
      setStartDate('');
      setDeadline('');
      setError('');
      setPathTemplates([]);
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!selectedPathId || !startDate || !deadline || !careerPath) {
      setError('Please fill in all fields');
      return;
    }

    if (new Date(deadline) <= new Date(startDate)) {
      setError('Deadline must be after start date');
      return;
    }

    setIsSubmitting(true);
    try {
      await progressApi.assignPath({
        userCareerPathId: careerPath.userCareerPathId,
        pathTemplateId: selectedPathId as number,
        startDate,
        deadline,
      });
      onSuccess();
      onClose();
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail || 'Failed to assign learning path');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const selectedPath = pathTemplates.find((p) => p.pathTemplateId === selectedPathId);

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-modal w-full max-w-lg">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Assign Learning Path</h2>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <LoadingSpinner size="lg" />
              </div>
            ) : (
              <>
                {error && (
                  <div className="p-4 bg-danger-50 border border-danger-200 rounded-lg text-danger-600 text-sm">
                    {error}
                  </div>
                )}

                {pathTemplates.length === 0 ? (
                  <div className="text-center py-8">
                    <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-500">All available learning paths have been assigned.</p>
                  </div>
                ) : (
                  <>
                    {/* Path Selection */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <BookOpen className="w-4 h-4 inline mr-2" />
                        Learning Path
                      </label>
                      <select
                        value={selectedPathId}
                        onChange={(e) => setSelectedPathId(Number(e.target.value) || '')}
                        className="input"
                        required
                      >
                        <option value="">Choose a learning path...</option>
                        {pathTemplates.map((path) => (
                          <option key={path.pathTemplateId} value={path.pathTemplateId}>
                            {path.name} ({path.durationHours}h)
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Path Description */}
                    {selectedPath && (
                      <div className="p-4 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-600">{selectedPath.description}</p>
                        <p className="text-xs text-gray-400 mt-2">
                          Estimated duration: {selectedPath.durationHours} hours
                        </p>
                      </div>
                    )}

                    {/* Date Range */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          <Calendar className="w-4 h-4 inline mr-2" />
                          Start Date
                        </label>
                        <input
                          type="date"
                          value={startDate}
                          onChange={(e) => setStartDate(e.target.value)}
                          className="input"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          <Calendar className="w-4 h-4 inline mr-2" />
                          Deadline
                        </label>
                        <input
                          type="date"
                          value={deadline}
                          onChange={(e) => setDeadline(e.target.value)}
                          className="input"
                          required
                        />
                      </div>
                    </div>
                  </>
                )}
              </>
            )}

            {/* Actions */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
              <button
                type="button"
                onClick={onClose}
                className="btn bg-gray-100 text-gray-700 hover:bg-gray-200"
                disabled={isSubmitting}
              >
                Cancel
              </button>
              {pathTemplates.length > 0 && (
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isLoading || isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <LoadingSpinner size="sm" />
                      Assigning...
                    </>
                  ) : (
                    'Assign Path'
                  )}
                </button>
              )}
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
