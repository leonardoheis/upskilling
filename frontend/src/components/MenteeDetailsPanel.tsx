import { useEffect } from 'react';
import { X, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import type { MenteeProgressSummary } from '../types';

interface MenteeDetailsPanelProps {
  isOpen: boolean;
  onClose: () => void;
  mentee: MenteeProgressSummary | null;
}

export default function MenteeDetailsPanel({
  isOpen,
  onClose,
  mentee,
}: MenteeDetailsPanelProps) {
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="!fixed !inset-0 !m-0 bg-black/50 z-[9998] transition-opacity"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="!fixed !inset-y-0 !right-0 !m-0 w-full max-w-2xl bg-white shadow-modal z-[9999] transform transition-transform duration-300 ease-out overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 flex-shrink-0">
          <h2 className="text-xl font-semibold text-gray-900">Mentee Details</h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {mentee ? (
            <div className="space-y-6">
              {/* Mentee Info Card */}
              <div className="bg-gray-50 rounded-xl p-5">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-primary-500 flex items-center justify-center flex-shrink-0">
                    <span className="text-white font-semibold text-2xl">
                      {mentee.fullName.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">{mentee.fullName}</h3>
                    <p className="text-sm text-gray-500">{mentee.email}</p>
                    <p className="text-sm text-primary-500 font-medium mt-1">{mentee.careerName}</p>
                  </div>
                </div>

                {/* Progress Overview */}
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-2xl font-bold text-gray-900">{mentee.overallProgressPercent}%</p>
                      <p className="text-xs text-gray-500">Overall Progress</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-900">
                        {mentee.pathsCompleted}/{mentee.pathsTotal}
                      </p>
                      <p className="text-xs text-gray-500">Paths Completed</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-warning-500">{mentee.pendingValidation}</p>
                      <p className="text-xs text-gray-500">Pending Validation</p>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mt-4">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-500">Progress</span>
                      <span className="font-medium text-gray-900">{mentee.overallProgressPercent}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${mentee.overallProgressPercent}%` }}
                      />
                    </div>
                  </div>

                  {/* Timeline */}
                  <div className="mt-4 flex justify-between text-sm">
                    <div>
                      <p className="text-gray-400">Start Date</p>
                      <p className="text-gray-900 font-medium">{formatDate(mentee.startDate)}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-gray-400">End Date</p>
                      <p className="text-gray-900 font-medium">{formatDate(mentee.endDate)}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Career Path Section */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    My Assigned Career Path: {mentee.careerName}
                  </h3>
                </div>

                <p className="text-sm text-gray-500 mb-4">
                  Complete all assigned paths and courses. Start date: {formatDate(mentee.startDate)}, Deadline: {formatDate(mentee.endDate)}
                </p>

                {/* Note about adding paths */}
                <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 mb-4">
                  <p className="text-sm text-primary-700">
                    <strong>Note:</strong> To add learning paths to this career track, the system requires an API endpoint to fetch individual mentee career paths. 
                    Learning paths can be managed from the Development Plans page.
                  </p>
                </div>

                {/* Paths Table Placeholder */}
                <div className="border border-gray-200 rounded-xl overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                          Path #
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                          Path Name
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                          Progress
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                          Validation
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {/* Placeholder rows showing mentee's progress */}
                      <tr>
                        <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                          <Clock className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                          <p>Path details require fetching from the mentee's career path endpoint.</p>
                          <p className="text-sm text-gray-400 mt-1">
                            Currently showing: {mentee.pathsCompleted} completed, {mentee.pathsTotal - mentee.pathsCompleted} remaining
                          </p>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Quick Stats Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="border border-gray-200 rounded-xl p-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-success-100 flex items-center justify-center">
                      <CheckCircle className="w-5 h-5 text-success-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-900">{mentee.pathsCompleted}</p>
                      <p className="text-xs text-gray-500">Paths Completed</p>
                    </div>
                  </div>
                </div>
                <div className="border border-gray-200 rounded-xl p-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-warning-100 flex items-center justify-center">
                      <AlertCircle className="w-5 h-5 text-warning-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-900">{mentee.pendingValidation}</p>
                      <p className="text-xs text-gray-500">Awaiting Validation</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">No mentee selected</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
