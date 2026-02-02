import { useEffect, useState, useCallback } from 'react';
import { teamsApi, progressApi } from '../services/api';
import type { TeamWithMembers, MenteeProgressSummary, TeamMember } from '../types';
import { UserPlus, Users } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import StatusBadge from '../components/StatusBadge';
import AssignCareerPathModal from '../components/AssignCareerPathModal';
import MenteeDetailsPanel from '../components/MenteeDetailsPanel';
import ActionMenu from '../components/ActionMenu';

export default function TeamManagementPage() {
  const [teams, setTeams] = useState<TeamWithMembers[]>([]);
  const [teamProgress, setTeamProgress] = useState<MenteeProgressSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Modal and panel state
  const [showAssignCareerModal, setShowAssignCareerModal] = useState(false);
  const [showMenteePanel, setShowMenteePanel] = useState(false);
  const [selectedMentee, setSelectedMentee] = useState<MenteeProgressSummary | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const [teamsData, progressData] = await Promise.all([
        teamsApi.getMyTeams(),
        progressApi.getTeamProgress(),
      ]);
      setTeams(teamsData);
      setTeamProgress(progressData);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleAssignCareerSuccess = () => {
    fetchData();
  };

  const handleViewMenteeDetails = (member: MenteeProgressSummary) => {
    setSelectedMentee(member);
    setShowMenteePanel(true);
  };

  const handleRemoveMentee = async (userId: number) => {
    // Find which team this user belongs to
    const team = teams.find((t) => t.members.some((m) => m.userId === userId));
    if (!team) {
      console.error('Team not found for user');
      return;
    }

    if (!confirm('Are you sure you want to remove this mentee from the team?')) {
      return;
    }

    try {
      await teamsApi.removeMember(team.teamId, userId);
      fetchData();
    } catch (error) {
      console.error('Failed to remove mentee:', error);
      alert('Failed to remove mentee. Please try again.');
    }
  };

  // Get all unique team members for the assign modal
  const allTeamMembers: TeamMember[] = teams.reduce((acc: TeamMember[], team) => {
    team.members.forEach((member) => {
      if (!acc.find((m) => m.userId === member.userId)) {
        acc.push(member);
      }
    });
    return acc;
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Calculate overview metrics
  const avgProgress = teamProgress.length > 0
    ? Math.round(teamProgress.reduce((sum, p) => sum + p.overallProgressPercent, 0) / teamProgress.length)
    : 0;
  
  const totalPathsCompleted = teamProgress.reduce((sum, p) => sum + p.pathsCompleted, 0);
  const totalPaths = teamProgress.reduce((sum, p) => sum + p.pathsTotal, 0);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Team Management</h1>
        <p className="mt-1 text-gray-500">
          Manage your team members, assign career paths, set deadlines, and track progress
        </p>
      </div>

      {teams.length === 0 ? (
        <div className="card text-center py-12">
          <div className="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center mx-auto mb-4">
            <Users className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No teams yet</h3>
          <p className="text-gray-500">You don't manage any teams currently.</p>
        </div>
      ) : (
        <>
          {/* Mentees Section */}
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">Mentees</h2>
              <button 
                className="btn btn-primary"
                onClick={() => setShowAssignCareerModal(true)}
              >
                <UserPlus className="w-4 h-4" />
                Add Mentee
              </button>
            </div>

            {teamProgress.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">
                  No mentees with development plans yet.
                </p>
                <button
                  className="btn btn-primary"
                  onClick={() => setShowAssignCareerModal(true)}
                >
                  <UserPlus className="w-4 h-4" />
                  Assign Development Plan
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {teamProgress.map((member) => (
                  <div
                    key={member.userId}
                    className="border border-gray-200 rounded-xl p-5 hover:shadow-card-hover transition-shadow relative"
                  >
                    {/* Action Menu */}
                    <div className="absolute top-3 right-3">
                      <ActionMenu
                        items={[
                          {
                            label: 'View Details',
                            onClick: () => handleViewMenteeDetails(member),
                          },
                          {
                            label: 'Remove from Team',
                            onClick: () => handleRemoveMentee(member.userId),
                            danger: true,
                          },
                        ]}
                      />
                    </div>

                    {/* Avatar and Info */}
                    <div className="flex items-center gap-3 mb-4 pr-8">
                      <div className="w-12 h-12 rounded-full bg-primary-500 flex items-center justify-center flex-shrink-0">
                        <span className="text-white font-semibold text-lg">
                          {member.fullName.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div className="min-w-0">
                        <h3 className="font-semibold text-gray-900 truncate">{member.fullName}</h3>
                        <p className="text-sm text-gray-500 truncate">{member.email}</p>
                        <p className="text-sm text-gray-400">{member.careerName}</p>
                      </div>
                    </div>

                    {/* Stats */}
                    <div className="space-y-2 mb-4">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">Paths Completed</span>
                        <span className="font-medium text-gray-900">
                          {member.pathsCompleted}/{member.pathsTotal}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">Overall Progress</span>
                        <span className="font-medium text-gray-900">
                          {member.overallProgressPercent}%
                        </span>
                      </div>
                      <div className="flex justify-between text-sm items-center">
                        <span className="text-gray-500">Status</span>
                        <StatusBadge status={member.overallProgressPercent === 100 ? 'completed' : 'in_progress'} />
                      </div>
                    </div>

                    {/* Action Button */}
                    <button 
                      className="w-full btn btn-primary flex items-center justify-center gap-2"
                      onClick={() => handleViewMenteeDetails(member)}
                    >
                      <Users className="w-4 h-4" />
                      View Mentee Details
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Mentees Progress Overview */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">Mentees Progress Overview</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Average Progress */}
              <div className="text-center p-6 border border-gray-200 rounded-xl">
                <p className="text-sm text-gray-500 mb-3">Mentees Average Progress</p>
                <div className="w-full bg-gray-200 rounded-full h-3 mb-3">
                  <div
                    className="bg-primary-500 h-3 rounded-full transition-all duration-500"
                    style={{ width: `${avgProgress}%` }}
                  />
                </div>
                <p className="text-2xl font-bold text-primary-500">{avgProgress}%</p>
              </div>

              {/* Paths Completed */}
              <div className="text-center p-6 border border-gray-200 rounded-xl">
                <p className="text-sm text-gray-500 mb-3">Paths Completed</p>
                <p className="text-2xl font-bold text-primary-500">
                  {totalPathsCompleted}/{totalPaths}
                </p>
                <p className="text-sm text-gray-400 mt-1">Average per mentee</p>
              </div>

              {/* Total Mentees */}
              <div className="text-center p-6 border border-gray-200 rounded-xl">
                <p className="text-sm text-gray-500 mb-3">Total Mentees</p>
                <p className="text-2xl font-bold text-primary-500">{teamProgress.length}</p>
                <p className="text-sm text-gray-400 mt-1">Active assignments</p>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Assign Career Path Modal */}
      <AssignCareerPathModal
        isOpen={showAssignCareerModal}
        onClose={() => setShowAssignCareerModal(false)}
        onSuccess={handleAssignCareerSuccess}
        teamMembers={allTeamMembers}
      />

      {/* Mentee Details Panel */}
      <MenteeDetailsPanel
        isOpen={showMenteePanel}
        onClose={() => setShowMenteePanel(false)}
        mentee={selectedMentee}
      />
    </div>
  );
}
