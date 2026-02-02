import { useState, useEffect } from 'react';
import { X, Calendar, User, Briefcase } from 'lucide-react';
import { careersApi, progressApi } from '../services/api';
import type { Career, TeamMember } from '../types';
import LoadingSpinner from './LoadingSpinner';

interface AssignCareerPathModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  teamMembers: TeamMember[];
}

export default function AssignCareerPathModal({
  isOpen,
  onClose,
  onSuccess,
  teamMembers,
}: AssignCareerPathModalProps) {
  const [careers, setCareers] = useState<Career[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<number | ''>('');
  const [selectedCareerId, setSelectedCareerId] = useState<number | ''>('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Fetch careers on mount
  useEffect(() => {
    if (isOpen) {
      const fetchCareers = async () => {
        setIsLoading(true);
        try {
          const response = await careersApi.list(1, 100);
          setCareers(response.items);
        } catch (err) {
          console.error('Failed to fetch careers:', err);
          setError('Failed to load careers');
        } finally {
          setIsLoading(false);
        }
      };
      fetchCareers();

      // Set default dates
      const today = new Date();
      const sixMonthsLater = new Date(today);
      sixMonthsLater.setMonth(sixMonthsLater.getMonth() + 6);
      setStartDate(today.toISOString().split('T')[0]);
      setEndDate(sixMonthsLater.toISOString().split('T')[0]);
    }
  }, [isOpen]);

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setSelectedUserId('');
      setSelectedCareerId('');
      setStartDate('');
      setEndDate('');
      setError('');
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!selectedUserId || !selectedCareerId || !startDate || !endDate) {
      setError('Please fill in all fields');
      return;
    }

    if (new Date(endDate) <= new Date(startDate)) {
      setError('End date must be after start date');
      return;
    }

    setIsSubmitting(true);
    try {
      await progressApi.assignCareerPath({
        userId: selectedUserId as number,
        careerId: selectedCareerId as number,
        startDate,
        endDate,
      });
      onSuccess();
      onClose();
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail || 'Failed to assign career path');
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

  return (
    <>
      {/* Backdrop */}
      <div
        className="!fixed !inset-0 !m-0 bg-black/50 z-[9998] transition-opacity"
        onClick={onClose}
      />

      {/* Slide-out Panel */}
      <div className="!fixed !inset-y-0 !right-0 !m-0 w-full max-w-md bg-white shadow-modal z-[9999] transform transition-transform duration-300 ease-out overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 flex-shrink-0">
          <h2 className="text-xl font-semibold text-gray-900">Assign Development Plan</h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6">
          <div className="space-y-6">
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

                {/* Mentee Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <User className="w-4 h-4 inline mr-2" />
                    Select Mentee
                  </label>
                  <select
                    value={selectedUserId}
                    onChange={(e) => setSelectedUserId(Number(e.target.value) || '')}
                    className="input"
                    required
                  >
                    <option value="">Choose a team member...</option>
                    {teamMembers.map((member) => (
                      <option key={member.userId} value={member.userId}>
                        {member.fullName} ({member.email})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Career Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Briefcase className="w-4 h-4 inline mr-2" />
                    Career Track
                  </label>
                  <select
                    value={selectedCareerId}
                    onChange={(e) => setSelectedCareerId(Number(e.target.value) || '')}
                    className="input"
                    required
                  >
                    <option value="">Choose a career track...</option>
                    {careers.map((career) => (
                      <option key={career.careerId} value={career.careerId}>
                        {career.name}
                        {career.specialization && ` - ${career.specialization}`}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Date Range */}
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
                    End Date
                  </label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="input"
                    required
                  />
                </div>
              </>
            )}
          </div>
        </form>

        {/* Actions - Fixed at bottom */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 flex-shrink-0">
          <button
            type="button"
            onClick={onClose}
            className="btn bg-gray-100 text-gray-700 hover:bg-gray-200"
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            className="btn btn-primary"
            disabled={isLoading || isSubmitting}
          >
            {isSubmitting ? (
              <>
                <LoadingSpinner size="sm" />
                Assigning...
              </>
            ) : (
              'Assign Development Plan'
            )}
          </button>
        </div>
      </div>
    </>
  );
}
