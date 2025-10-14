import React from 'react';
import { ArrowLeft, BarChart3, Users, Award, TrendingUp, Building, BookOpen } from 'lucide-react';

const Statistics = ({ onNavigateBack }) => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={onNavigateBack}
            className="flex items-center text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 mb-6 font-medium transition-colors"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Home
          </button>
          
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Faculty Research Statistics
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            Comprehensive analytics and insights across academic departments
          </p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Faculty</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">206</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Citations</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">12.5K</p>
              </div>
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-xl flex items-center justify-center">
                <Award className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Publications</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">3.2K</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-xl flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Departments</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">15</p>
              </div>
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-xl flex items-center justify-center">
                <Building className="w-6 h-6 text-orange-600 dark:text-orange-400" />
              </div>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Research Areas Distribution */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center mb-6">
              <BarChart3 className="w-6 h-6 text-blue-600 dark:text-blue-400 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Research Areas Distribution</h2>
            </div>
            <div className="space-y-4">
              {[
                { area: 'Artificial Intelligence', count: 45, percentage: 22 },
                { area: 'Computer Science', count: 38, percentage: 18 },
                { area: 'Data Science', count: 32, percentage: 16 },
                { area: 'Machine Learning', count: 28, percentage: 14 },
                { area: 'Cybersecurity', count: 24, percentage: 12 },
                { area: 'Software Engineering', count: 20, percentage: 10 },
                { area: 'Other Areas', count: 19, percentage: 8 }
              ].map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{item.area}</span>
                  <div className="flex items-center gap-3">
                    <div className="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${item.percentage * 4}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-600 dark:text-gray-400 w-8">{item.count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Performers */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center mb-6">
              <TrendingUp className="w-6 h-6 text-green-600 dark:text-green-400 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Top Cited Faculty</h2>
            </div>
            <div className="space-y-4">
              {[
                { name: 'Dr. Sarah Johnson', citations: 1250, hIndex: 45 },
                { name: 'Prof. Michael Chen', citations: 1180, hIndex: 42 },
                { name: 'Dr. Emily Rodriguez', citations: 1050, hIndex: 38 },
                { name: 'Prof. David Kim', citations: 980, hIndex: 35 },
                { name: 'Dr. Lisa Wang', citations: 920, hIndex: 33 }
              ].map((faculty, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-xl">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{faculty.name}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">h-index: {faculty.hIndex}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-blue-600 dark:text-blue-400">{faculty.citations}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">citations</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Coming Soon Message */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            More Analytics Coming Soon
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            We're working on advanced analytics including collaboration networks, research trends, and predictive insights.
          </p>
          <div className="flex justify-center space-x-4">
            <span className="px-4 py-2 bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300 rounded-full text-sm">
              Collaboration Networks
            </span>
            <span className="px-4 py-2 bg-purple-100 dark:bg-purple-900/40 text-purple-800 dark:text-purple-300 rounded-full text-sm">
              Research Trends
            </span>
            <span className="px-4 py-2 bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300 rounded-full text-sm">
              Impact Analysis
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Statistics;