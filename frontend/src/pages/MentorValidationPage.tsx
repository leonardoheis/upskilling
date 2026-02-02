import { useEffect, useState } from 'react';
import { progressApi } from '../services/api';
import type { UserPathAssignmentDetail } from '../types';
import { CheckCircle, XCircle, Clock, User, Calendar, ChevronDown, ChevronUp } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import StatusBadge from '../components/StatusBadge';

export default function MentorValidationPage() {
  const [pendingAssignments, setPendingAssignments] = useState<UserPathAssignmentDetail[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  useEffect(() => {
    fetchPendingValidations();
  }, []);

  const fetchPendingValidations = async () => {
    try {
      const data = await progressApi.getPendingValidations();
      setPendingAssignments(data);
    } catch (error) {
      console.error('Failed to fetch pending validations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async (assignmentId: number) => {
    setActionLoading(assignmentId);
    try {
      await progressApi.approveAssignment(assignmentId);
      setPendingAssignments((prev) =>
        prev.filter((a) => a.userPathAssignmentId !== assignmentId)
      );
    } catch (error) {
      console.error('Failed to approve:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (assignmentId: number) => {
    setActionLoading(assignmentId);
    try {
      await progressApi.rejectAssignment(assignmentId);
      setPendingAssignments((prev) =>
        prev.filter((a) => a.userPathAssignmentId !== assignmentId)
      );
    } catch (error) {
      console.error('Failed to reject:', error);
    } finally {
      setActionLoading(null);
    }
  };

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
        <h1 className="text-2xl font-bold text-gray-900">Mentor Validation</h1>
        <p className="mt-1 text-gray-500">
          Review and validate completed learning paths from your mentees.
        </p>
      </div>

      {/* Stats */}
      <div className="card">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-warning-100 flex items-center justify-center">
            <Clock className="w-6 h-6 text-warning-500" />
          </div>
          <div>
            <p className="text-gray-500 text-sm">Pending Validations</p>
            <p className="text-2xl font-bold text-gray-900">{pendingAssignments.length}</p>
          </div>
        </div>
      </div>

      {/* Pending validations list */}
      {pendingAssignments.length === 0 ? (
        <div className="card text-center py-12">
          <div className="w-16 h-16 rounded-2xl bg-success-100 flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-success-500" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">All caught up!</h3>
          <p className="text-gray-500">No pending validations at the moment.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {pendingAssignments.map((assignment) => (
            <div key={assignment.userPathAssignmentId} className="card">
              <div
                className="flex items-start justify-between cursor-pointer"
                onClick={() =>
                  setExpandedId(
                    expandedId === assignment.userPathAssignmentId
                      ? null
                      : assignment.userPathAssignmentId
                  )
                }
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center">
                    <User className="w-6 h-6 text-primary-500" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {assignment.pathTemplate?.name || `Path #${assignment.pathTemplateId}`}
                    </h3>
                    <p className="text-gray-500 text-sm">
                      Completed on {new Date(assignment.deadline).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <StatusBadge status="pending">Pending Review</StatusBadge>
                  {expandedId === assignment.userPathAssignmentId ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </div>
              </div>

              {/* Expanded details */}
              {expandedId === assignment.userPathAssignmentId && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  {/* Assignment details */}
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-500 text-sm">Start:</span>
                      <span className="text-gray-900 text-sm">
                        {new Date(assignment.startDate).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-500 text-sm">Deadline:</span>
                      <span className="text-gray-900 text-sm">
                        {new Date(assignment.deadline).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  {/* Step progress */}
                  {assignment.stepProgress && assignment.stepProgress.length > 0 && (
                    <div className="mb-6">
                      <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">
                        Completed Steps
                      </h4>
                      <div className="space-y-2">
                        {assignment.stepProgress.map((sp) => (
                          <div
                            key={sp.userStepProgressId}
                            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                          >
                            <div className="flex items-center gap-3">
                              <CheckCircle className="w-4 h-4 text-success-500" />
                              <span className="text-gray-900 text-sm">
                                {sp.step?.name || `Step #${sp.stepId}`}
                              </span>
                            </div>
                            <span className="text-gray-500 text-sm">{sp.progressPercent}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Action buttons */}
                  <div className="flex items-center gap-3">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleApprove(assignment.userPathAssignmentId);
                      }}
                      disabled={actionLoading === assignment.userPathAssignmentId}
                      className="btn btn-primary flex items-center gap-2"
                    >
                      {actionLoading === assignment.userPathAssignmentId ? (
                        <LoadingSpinner size="sm" />
                      ) : (
                        <CheckCircle className="w-4 h-4" />
                      )}
                      Approve
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleReject(assignment.userPathAssignmentId);
                      }}
                      disabled={actionLoading === assignment.userPathAssignmentId}
                      className="btn btn-danger flex items-center gap-2"
                    >
                      <XCircle className="w-4 h-4" />
                      Reject
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
