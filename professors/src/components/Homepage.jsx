import React from 'react';
import { BarChart3, Users, GraduationCap, Search } from 'lucide-react';

const Homepage = ({ onNavigate }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="flex flex-col items-center justify-center min-h-screen px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <GraduationCap className="w-16 h-16 text-blue-600 dark:text-blue-400 mr-4" />
            <h1 className="text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 leading-tight">
              Samsung Prism
            </h1>
          </div>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto leading-relaxed">
            AI-Powered Faculty Research Directory & Analytics Platform
          </p>
          <p className="text-lg text-gray-500 dark:text-gray-400 mt-2">
            Discover academic expertise and research insights
          </p>
        </div>

        {/* Navigation Buttons */}
        <div className="flex flex-col sm:flex-row gap-6 w-full max-w-2xl">
          {/* Statistics Button */}
          <button
            onClick={() => onNavigate('statistics')}
            className="group flex-1 bg-white dark:bg-gray-800 rounded-2xl shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 p-8 border border-gray-200 dark:border-gray-700"
          >
            <div className="flex flex-col items-center text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                <BarChart3 className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Statistics
              </h2>
              <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                View comprehensive analytics, research metrics, and faculty insights across departments
              </p>
            </div>
          </button>

          {/* Faculty Search Button */}
          <button
            onClick={() => onNavigate('faculty-search')}
            className="group flex-1 bg-white dark:bg-gray-800 rounded-2xl shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 p-8 border border-gray-200 dark:border-gray-700"
          >
            <div className="flex flex-col items-center text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                <Search className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Faculty Search
              </h2>
              <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                AI-powered search to find faculty experts by research domain, skills, and expertise
              </p>
            </div>
          </button>
        </div>

        {/* Features Overview */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl w-full">
          <div className="text-center p-6 bg-white/50 dark:bg-gray-800/50 rounded-xl backdrop-blur-sm">
            <Users className="w-8 h-8 text-blue-600 dark:text-blue-400 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Faculty Profiles</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Comprehensive profiles with research interests, publications, and academic metrics
            </p>
          </div>
          
          <div className="text-center p-6 bg-white/50 dark:bg-gray-800/50 rounded-xl backdrop-blur-sm">
            <Search className="w-8 h-8 text-purple-600 dark:text-purple-400 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Smart Search</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Natural language AI search to find experts by skills and research domains
            </p>
          </div>
          
          <div className="text-center p-6 bg-white/50 dark:bg-gray-800/50 rounded-xl backdrop-blur-sm">
            <BarChart3 className="w-8 h-8 text-green-600 dark:text-green-400 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Analytics</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Research trends, publication metrics, and institutional insights
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-16 text-center">
          <p className="text-gray-500 dark:text-gray-400 text-sm">
            Powered by AI • Built for Academic Excellence
          </p>
        </div>
      </div>
    </div>
  );
};

export default Homepage;