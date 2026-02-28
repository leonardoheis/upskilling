import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/useAuth';
import { progressApi } from '../services/api';
import type { DashboardStats } from '../types';
import { TrendingUp, Target, Award, Clock, BookOpen, GraduationCap, User } from 'lucide-react';
import { Link } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await progressApi.getDashboard();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch dashboard stats:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome section */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.fullName?.split(' ')[0]}!
        </h1>
        <p className="mt-1 text-gray-500">
          Track your progress and continue your career development journey.
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card card-hover">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-primary-500" />
            </div>
            <div>
              <p className="text-gray-500 text-sm">Overall Progress</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.overallProgress || 0}%</p>
            </div>
          </div>
          <div className="mt-4 progress-bar">
            <div
              className="progress-bar-fill"
              style={{ width: `${stats?.overallProgress || 0}%` }}
            />
          </div>
        </div>

        <div className="card card-hover">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center">
              <Target className="w-6 h-6 text-primary-500" />
            </div>
            <div>
              <p className="text-gray-500 text-sm">Current Path</p>
              <p className="text-lg font-semibold text-gray-900 truncate max-w-[150px]">
                {stats?.currentPath || 'No active path'}
              </p>
            </div>
          </div>
          <div className="mt-4 progress-bar">
            <div
              className="progress-bar-fill"
              style={{ width: `${stats?.currentPathProgress || 0}%` }}
            />
          </div>
        </div>

        <div className="card card-hover">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-success-100 flex items-center justify-center">
              <Award className="w-6 h-6 text-success-500" />
            </div>
            <div>
              <p className="text-gray-500 text-sm">Skills Obtained</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.skillsObtained || 0}</p>
            </div>
          </div>
        </div>

        <div className="card card-hover">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center">
              <Clock className="w-6 h-6 text-gray-500" />
            </div>
            <div>
              <p className="text-gray-500 text-sm">Paths Remaining</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.pathsRemaining || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Current career */}
      {stats?.currentCareer && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Current Career Track</h2>
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-primary-100 flex items-center justify-center">
              <Target className="w-7 h-7 text-primary-500" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900">{stats.currentCareer}</h3>
              <p className="text-gray-500">
                {stats.currentPath
                  ? `Currently working on: ${stats.currentPath}`
                  : 'Ready to start your next path'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Quick actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          to="/development-plans"
          className="card card-hover group cursor-pointer"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center group-hover:bg-primary-200 transition-colors">
              <BookOpen className="w-6 h-6 text-primary-500" />
            </div>
            <div>
              <h3 className="text-gray-900 font-medium group-hover:text-primary-500 transition-colors">
                View Development Plans
              </h3>
              <p className="text-gray-500 text-sm">Track your assigned paths</p>
            </div>
          </div>
        </Link>

        <Link
          to="/learning-paths"
          className="card card-hover group cursor-pointer"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center group-hover:bg-primary-200 transition-colors">
              <GraduationCap className="w-6 h-6 text-primary-500" />
            </div>
            <div>
              <h3 className="text-gray-900 font-medium group-hover:text-primary-500 transition-colors">
                Browse Learning Paths
              </h3>
              <p className="text-gray-500 text-sm">Explore available courses</p>
            </div>
          </div>
        </Link>

        <Link
          to="/my-bio"
          className="card card-hover group cursor-pointer"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center group-hover:bg-gray-200 transition-colors">
              <User className="w-6 h-6 text-gray-500" />
            </div>
            <div>
              <h3 className="text-gray-900 font-medium group-hover:text-gray-700 transition-colors">
                Update Profile
              </h3>
              <p className="text-gray-500 text-sm">Manage your bio and settings</p>
            </div>
          </div>
        </Link>
      </div>
    </div>
  );
}
