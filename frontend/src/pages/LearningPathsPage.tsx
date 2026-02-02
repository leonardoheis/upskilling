import { useEffect, useState } from 'react';
import { careersApi, pathsApi } from '../services/api';
import type { Career, PathTemplate } from '../types';
import { Clock, BookOpen, ChevronRight, Filter } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

export default function LearningPathsPage() {
  const [careers, setCareers] = useState<Career[]>([]);
  const [paths, setPaths] = useState<PathTemplate[]>([]);
  const [selectedCareer, setSelectedCareer] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [careersRes, pathsRes] = await Promise.all([
          careersApi.list(1, 100),
          pathsApi.list(1, 100),
        ]);
        setCareers(careersRes.items);
        setPaths(pathsRes.items);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const filteredPaths = selectedCareer
    ? paths.filter((p) => p.careerId === selectedCareer)
    : paths;

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
        <h1 className="text-2xl font-bold text-gray-900">Learning Paths</h1>
        <p className="mt-1 text-gray-500">
          Explore available learning paths and courses for your career development.
        </p>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2 text-gray-500">
          <Filter className="w-4 h-4" />
          <span className="text-sm font-medium">Filter by career:</span>
        </div>
        <button
          onClick={() => setSelectedCareer(null)}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors border ${
            selectedCareer === null
              ? 'bg-primary-500 text-white border-primary-500'
              : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
          }`}
        >
          All Paths
        </button>
        {careers.map((career) => (
          <button
            key={career.careerId}
            onClick={() => setSelectedCareer(career.careerId)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors border ${
              selectedCareer === career.careerId
                ? 'bg-primary-500 text-white border-primary-500'
                : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
            }`}
          >
            {career.name}
          </button>
        ))}
      </div>

      {/* Paths grid */}
      {filteredPaths.length === 0 ? (
        <div className="card text-center py-12">
          <div className="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center mx-auto mb-4">
            <BookOpen className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No paths found</h3>
          <p className="text-gray-500">
            {selectedCareer
              ? 'No learning paths available for this career yet.'
              : 'No learning paths available.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPaths.map((path) => {
            const career = careers.find((c) => c.careerId === path.careerId);
            return (
              <div
                key={path.pathTemplateId}
                className="card card-hover group cursor-pointer"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center">
                    <BookOpen className="w-6 h-6 text-primary-500" />
                  </div>
                  <span className="px-3 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-full">
                    {career?.name || 'Unknown'}
                  </span>
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-primary-500 transition-colors">
                  {path.name}
                </h3>
                <p className="text-gray-500 text-sm mb-4 line-clamp-2">{path.description}</p>

                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <div className="flex items-center gap-2 text-gray-500">
                    <Clock className="w-4 h-4" />
                    <span className="text-sm">{path.durationHours} hours</span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-primary-500 transition-colors" />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
