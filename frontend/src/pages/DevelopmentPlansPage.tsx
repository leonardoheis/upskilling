import { useEffect, useState } from 'react';
import { progressApi } from '../services/api';
import type { UserCareerPathDetail, UserPathAssignment } from '../types';
import { ExternalLink, Eye, Check, Plus } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import StatusBadge from '../components/StatusBadge';
import ActionMenu from '../components/ActionMenu';
import SlideOutPanel from '../components/SlideOutPanel';

export default function DevelopmentPlansPage() {
  const [careerPaths, setCareerPaths] = useState<UserCareerPathDetail[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedAssignment, setSelectedAssignment] = useState<UserPathAssignment | null>(null);
  const [isPanelOpen, setIsPanelOpen] = useState(false);

  useEffect(() => {
    const fetchPaths = async () => {
      try {
        const data = await progressApi.getCareerPaths();
        setCareerPaths(data);
      } catch (error) {
        console.error('Failed to fetch career paths:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPaths();
  }, []);

  const handleViewDetails = (assignment: UserPathAssignment) => {
    setSelectedAssignment(assignment);
    setIsPanelOpen(true);
  };

  const handleMarkCompleted = (assignment: UserPathAssignment) => {
    // TODO: Implement mark as completed
    console.log('Mark completed:', assignment);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Get current path (first in-progress assignment)
  const currentCareer = careerPaths[0];
  const currentPath = currentCareer?.pathAssignments?.find(a => a.status === 'In Progress');
  const pathsRemaining = currentCareer?.pathAssignments?.filter(a => a.status !== 'Completed').length || 0;
  const pathsCompleted = currentCareer?.pathAssignments?.filter(a => a.status === 'Completed').length || 0;

  return (
    <div className="space-y-8">
      {careerPaths.length === 0 ? (
        <div className="card text-center py-12">
          <div className="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">📋</span>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No development plans yet</h3>
          <p className="text-gray-500">
            Your mentor will assign you a career path to get started.
          </p>
        </div>
      ) : (
        <>
          {/* Career Overview Card */}
          {currentCareer && (
            <div className="card">
              {/* Career Title */}
              <h1 className="text-2xl font-bold text-gray-900 mb-1">
                {currentCareer.careerName}
              </h1>
              {currentCareer.careerSpecialization && (
                <p className="text-gray-500 mb-6">
                  Specialization: {currentCareer.careerSpecialization}
                </p>
              )}

              {/* Overall Progress */}
              <div className="mb-8">
                <p className="text-sm text-gray-500 mb-2">Progress</p>
                <div className="w-full bg-gray-200 rounded-full h-3 mb-1">
                  <div
                    className="bg-gray-800 h-3 rounded-full transition-all duration-500"
                    style={{ width: `${currentCareer.overallProgressPercent}%` }}
                  />
                </div>
                <p className="text-sm text-gray-500">{currentCareer.overallProgressPercent}%</p>
              </div>

              {/* Current Path and Stats */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Current Path */}
                <div>
                  <p className="text-xs text-gray-400 uppercase tracking-wider mb-2">Current Path</p>
                  <h2 className="text-lg font-semibold text-gray-900 mb-3">
                    {currentPath ? `Path #${currentPath.pathTemplateId}` : 'No active path'}
                  </h2>
                  {currentPath && (
                    <>
                      <p className="text-sm text-gray-500 mb-2">Progress</p>
                      <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
                        <div
                          className="bg-primary-500 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${currentPath.progressPercent}%` }}
                        />
                      </div>
                      <p className="text-sm text-gray-500 mb-4">{currentPath.progressPercent}%</p>
                      <button className="btn btn-primary">
                        Continue Path
                      </button>
                    </>
                  )}
                </div>

                {/* Stats */}
                <div className="space-y-6">
                  <div>
                    <p className="text-xs text-gray-400 uppercase tracking-wider mb-2">Paths Remaining</p>
                    <p className="text-4xl font-bold text-gray-900">{pathsRemaining}</p>
                  </div>
                  <div className="border-t border-gray-200 pt-4">
                    <p className="text-xs text-gray-400 uppercase tracking-wider mb-2">Skills Obtained</p>
                    <p className="text-gray-500">-</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Assigned Paths Table */}
          {currentCareer && (
            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-xl font-semibold text-primary-500">
                  My Assigned Career Path: {currentCareer.careerName}
                </h2>
                <button className="btn btn-outline">
                  <Plus className="w-4 h-4" />
                  Add Path
                </button>
              </div>
              <p className="text-gray-500 text-sm mb-6">
                Complete all assigned paths and courses. Start date: {new Date(currentCareer.startDate).toLocaleDateString()}, 
                Deadline: {new Date(currentCareer.endDate).toLocaleDateString()}
              </p>

              {/* Table */}
              <div className="overflow-x-auto">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Path #</th>
                      <th>Path Name</th>
                      <th>Start Date</th>
                      <th>Deadline</th>
                      <th>Associated Paths</th>
                      <th>Mentor Validation</th>
                      <th>Link</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {currentCareer.pathAssignments.map((assignment, index) => (
                      <tr key={assignment.userPathAssignmentId}>
                        <td className="font-medium text-gray-900">
                          {index === currentCareer.pathAssignments.length - 1 ? 'Final' : index + 1}
                        </td>
                        <td>
                          <div>
                            <p className="font-semibold text-gray-900">
                              {index === currentCareer.pathAssignments.length - 1 
                                ? 'Final Project' 
                                : `Path #${assignment.pathTemplateId}`}
                            </p>
                            <p className="text-sm text-gray-500">
                              {index === currentCareer.pathAssignments.length - 1
                                ? 'Complete the final project for this career path'
                                : 'Learning path assignment'}
                            </p>
                          </div>
                        </td>
                        <td className="text-gray-600">
                          {new Date(assignment.startDate).toLocaleDateString()}
                        </td>
                        <td className="text-gray-600">
                          {new Date(assignment.deadline).toLocaleDateString()}
                        </td>
                        <td className="text-gray-500">
                          {index === 0 ? 'None' : index === currentCareer.pathAssignments.length - 1 ? 'All paths must be completed' : `Path #${currentCareer.pathAssignments[index - 1]?.pathTemplateId}`}
                        </td>
                        <td>
                          <StatusBadge 
                            status={
                              assignment.mentorValidationStatus === 'Approved' 
                                ? 'approved' 
                                : assignment.mentorValidationStatus === 'Rejected'
                                  ? 'rejected'
                                  : 'pending'
                            }
                          />
                        </td>
                        <td>
                          {index < currentCareer.pathAssignments.length - 1 && (
                            <a href="#" className="text-primary-500 hover:text-primary-600 flex items-center gap-1">
                              Open Course
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          )}
                          {index === currentCareer.pathAssignments.length - 1 && (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                        <td>
                          <ActionMenu
                            items={[
                              {
                                label: 'View Details',
                                onClick: () => handleViewDetails(assignment),
                                icon: <Eye className="w-4 h-4" />,
                              },
                              {
                                label: 'Mark Completed',
                                onClick: () => handleMarkCompleted(assignment),
                                icon: <Check className="w-4 h-4" />,
                              },
                            ]}
                          />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* Slide-out Panel for Path Details */}
      <SlideOutPanel
        isOpen={isPanelOpen}
        onClose={() => setIsPanelOpen(false)}
        title={`Path #${selectedAssignment?.pathTemplateId || ''}`}
      >
        {selectedAssignment && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">Path Information</h3>
            
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-gray-500">Path Number:</p>
                <p className="text-gray-900">{selectedAssignment.pathTemplateId}</p>
              </div>
              
              <div>
                <p className="text-sm font-medium text-gray-500">Description:</p>
                <p className="text-gray-900">Learning path assignment for career development.</p>
              </div>
              
              <div>
                <p className="text-sm font-medium text-gray-500">Duration:</p>
                <p className="text-gray-900">40 hours</p>
              </div>
              
              <div>
                <p className="text-sm font-medium text-gray-500">Start Date:</p>
                <p className="text-gray-900">{new Date(selectedAssignment.startDate).toLocaleDateString()}</p>
              </div>
              
              <div>
                <p className="text-sm font-medium text-gray-500">Deadline:</p>
                <p className="text-gray-900">{new Date(selectedAssignment.deadline).toLocaleDateString()}</p>
              </div>
              
              <div>
                <p className="text-sm font-medium text-gray-500">Associated Paths:</p>
                <p className="text-gray-900">None</p>
              </div>
              
              <div>
                <p className="text-sm font-medium text-gray-500">Mentor Validation:</p>
                <p className="text-gray-900">{selectedAssignment.mentorValidationStatus.toLowerCase()}</p>
              </div>
              
              <div>
                <p className="text-sm font-medium text-gray-500">Course Link:</p>
                <a href="#" className="text-primary-500 hover:text-primary-600">
                  https://learn.pwc.com/courses/path-{selectedAssignment.pathTemplateId}
                </a>
              </div>
            </div>

            <button 
              className="w-full btn btn-primary mt-8"
              onClick={() => {
                handleMarkCompleted(selectedAssignment);
                setIsPanelOpen(false);
              }}
            >
              Mark as Done
            </button>
          </div>
        )}
      </SlideOutPanel>
    </div>
  );
}
