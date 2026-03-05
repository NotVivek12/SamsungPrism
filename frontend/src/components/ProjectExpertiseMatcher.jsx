import React, { useState } from 'react';
import { 
  Search, FileText, Rocket, AlertCircle, CheckCircle, Award, 
  User, ChevronRight, ArrowRight, RefreshCw, X
} from 'lucide-react';
import aiSearchService from '../services/aiSearchService';

const ProjectExpertiseMatcher = () => {
  const [projectDescription, setProjectDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [matchingTeachers, setMatchingTeachers] = useState([]);
  const [showTeacherDetails, setShowTeacherDetails] = useState({});
  const [selectedExpertiseFilter, setSelectedExpertiseFilter] = useState('all');

  // Handle project description submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!projectDescription.trim()) {
      setError('Please provide a project description');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      setAnalysisResult(null);
      setMatchingTeachers([]);
      
      const data = await aiSearchService.analyzeProject(projectDescription);
      
      setAnalysisResult(data.analysis);
      setMatchingTeachers(data.professors || []);
    } catch (err) {
      console.error('Error analyzing project:', err);
      setError(err.message || 'An error occurred while analyzing your project');
    } finally {
      setLoading(false);
    }
  };
  
  // Filter teachers based on selected expertise
  const filteredTeachers = selectedExpertiseFilter === 'all' 
    ? matchingTeachers
    : matchingTeachers.filter(teacher => {
        return teacher.matching_domains.includes(selectedExpertiseFilter);
      });
  
  // Toggle teacher details visibility
  const toggleTeacherDetails = (teacherId) => {
    setShowTeacherDetails(prev => ({
      ...prev,
      [teacherId]: !prev[teacherId]
    }));
  };
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-cyan-500 font-sans tracking-tight mb-4 leading-[1.34]">
            Project-Based Faculty Matcher
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            Describe your project and we'll analyze it to find professors with the expertise you need
          </p>
        </div>
        
        {/* Project Description Form */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 mb-8 max-w-4xl mx-auto">
          <form onSubmit={handleSubmit}>
            <div className="mb-6">
              <label 
                htmlFor="project-description" 
                className="block text-lg font-semibold text-gray-800 dark:text-white mb-2"
              >
                Describe Your Project
              </label>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Provide details about your project goals, technical challenges, and the expertise you're looking for.
                Our AI will analyze your description to match you with professors who have relevant skills.
              </p>
              <textarea
                id="project-description"
                rows={6}
                placeholder="Example: I'm developing a machine learning application that can analyze medical images to detect early signs of retinal diseases. The project requires expertise in computer vision, deep learning for medical image processing, and knowledge of healthcare applications..."
                className="w-full p-4 border border-gray-300 dark:border-gray-600 rounded-lg
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                         focus:ring-2 focus:ring-blue-500 focus:border-transparent 
                         transition duration-300 shadow-inner resize-none"
                value={projectDescription}
                onChange={(e) => setProjectDescription(e.target.value)}
              ></textarea>
            </div>
            
            {error && (
              <div className="mb-4 p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg flex items-center gap-2">
                <AlertCircle className="w-5 h-5" />
                {error}
              </div>
            )}
            
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={loading || !projectDescription.trim()}
                className={`px-6 py-3 rounded-xl text-white font-semibold flex items-center gap-2 transition-all duration-300
                          ${loading || !projectDescription.trim()
                            ? 'bg-gray-400 dark:bg-gray-700 cursor-not-allowed'
                            : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-md hover:shadow-lg transform hover:scale-105'
                          }`}
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Rocket className="w-5 h-5" />
                    Analyze
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
        
        {/* Analysis Results Section */}
        {analysisResult && (
          <div className="space-y-8 max-w-6xl mx-auto">
            {/* AI Analysis Card */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-blue-100 dark:border-blue-900">
              <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                <FileText className="w-6 h-6 text-blue-500" />
                Project Analysis Results
              </h2>
              
              <div className="space-y-6">
                {/* Project Summary */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">Project Summary</h3>
                  <p className="text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
                    {analysisResult.summary}
                  </p>
                </div>
                
                {/* Required Expertise */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">Required Expertise Areas</h3>
                  <div className="flex flex-wrap gap-2">
                    {analysisResult.required_expertise.map((expertise, index) => (
                      <button
                        key={index}
                        onClick={() => setSelectedExpertiseFilter(expertise === selectedExpertiseFilter ? 'all' : expertise)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300
                                  ${expertise === selectedExpertiseFilter
                                    ? 'bg-blue-600 text-white shadow-md'
                                    : 'bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-200 hover:bg-blue-200 dark:hover:bg-blue-800'
                                  }`}
                      >
                        {expertise}
                      </button>
                    ))}
                  </div>
                </div>
                
                {/* Key Skills */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">Key Technical Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {analysisResult.key_skills.map((skill, index) => (
                      <span 
                        key={index} 
                        className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-full"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            
            {/* Matching Professors Section */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800 dark:text-white flex items-center gap-2">
                  <User className="w-6 h-6 text-blue-500" />
                  Matching Professors
                </h2>
                
                <div className="text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {selectedExpertiseFilter === 'all' 
                      ? `Showing all ${matchingTeachers.length} matches` 
                      : `Filtered by: ${selectedExpertiseFilter}`}
                  </span>
                  {selectedExpertiseFilter !== 'all' && (
                    <button 
                      onClick={() => setSelectedExpertiseFilter('all')}
                      className="ml-2 text-blue-600 hover:underline flex items-center gap-1"
                    >
                      <X className="w-3 h-3" /> Clear
                    </button>
                  )}
                </div>
              </div>
              
              {filteredTeachers.length > 0 ? (
                <div className="space-y-4">
                  {filteredTeachers.map((teacher) => (
                    <div 
                      key={teacher.id}
                      className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden hover:shadow-md transition-shadow duration-300"
                    >
                      {/* Teacher Summary Row */}
                      <div 
                        className="flex items-center gap-4 p-4 cursor-pointer bg-gray-50 dark:bg-gray-800"
                        onClick={() => toggleTeacherDetails(teacher.id)}
                      >
                        {/* Avatar */}
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                          {teacher.name ? teacher.name.split(' ').map(n => n[0]).join('').substring(0, 2) : '??'}
                        </div>
                        
                        {/* Basic Info */}
                        <div className="flex-1">
                          <div className="flex items-center gap-3">
                            <h3 className="font-semibold text-gray-900 dark:text-white">
                              {teacher.name}
                            </h3>
                            <div className="px-3 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs font-medium rounded-full">
                              {teacher.match_percentage}% match
                            </div>
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {teacher.college}
                          </p>
                        </div>
                        
                        {/* Matching Domains */}
                        <div className="hidden md:flex flex-wrap gap-2 max-w-md">
                          {teacher.matching_domains.slice(0, 3).map((domain, index) => (
                            <span 
                              key={index}
                              className="px-2 py-1 bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-200 text-xs rounded"
                            >
                              {domain}
                            </span>
                          ))}
                          {teacher.matching_domains.length > 3 && (
                            <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded">
                              +{teacher.matching_domains.length - 3} more
                            </span>
                          )}
                        </div>
                        
                        {/* Toggle Indicator */}
                        <ChevronRight 
                          className={`w-5 h-5 text-gray-400 transition-transform duration-300 ${showTeacherDetails[teacher.id] ? 'rotate-90' : ''}`} 
                        />
                      </div>
                      
                      {/* Expanded Details */}
                      {showTeacherDetails[teacher.id] && (
                        <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Left Column */}
                            <div className="space-y-4">
                              {/* Contact Info */}
                              <div>
                                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Contact Information</h4>
                                <div className="text-sm text-gray-600 dark:text-gray-400">
                                  <p className="mb-1">{teacher.email}</p>
                                  {teacher.profile_link && (
                                    <a 
                                      href={teacher.profile_link} 
                                      target="_blank" 
                                      rel="noopener noreferrer"
                                      className="text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                                    >
                                      Visit Profile <ArrowRight className="w-3 h-3" />
                                    </a>
                                  )}
                                </div>
                              </div>
                              
                              {/* Matching Expertise */}
                              <div>
                                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Matching Expertise Areas</h4>
                                <div className="flex flex-wrap gap-2">
                                  {teacher.matching_domains.map((domain, index) => (
                                    <div 
                                      key={index}
                                      className="flex items-center gap-1 px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 text-xs rounded"
                                    >
                                      <CheckCircle className="w-3 h-3" />
                                      {domain}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </div>
                            
                            {/* Right Column */}
                            <div className="space-y-4">
                              {/* Domain Expertise */}
                              <div>
                                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Research Domains</h4>
                                <div className="flex flex-wrap gap-2">
                                  {teacher.domain_expertise && teacher.domain_expertise.split(' | ').map((domain, index) => (
                                    <span 
                                      key={index}
                                      className={`px-2 py-1 text-xs rounded ${
                                        teacher.matching_domains.includes(domain.trim())
                                          ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
                                          : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                                      }`}
                                    >
                                      {domain.trim()}
                                    </span>
                                  ))}
                                </div>
                              </div>
                              
                              {/* Academic Profiles */}
                              <div>
                                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Academic Profiles</h4>
                                <div className="flex gap-2">
                                  {teacher.google_scholar_url && (
                                    <a 
                                      href={teacher.google_scholar_url} 
                                      target="_blank" 
                                      rel="noopener noreferrer"
                                      className="px-3 py-1.5 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 text-xs rounded-lg flex items-center gap-1 hover:bg-blue-100 dark:hover:bg-blue-800/30 transition-colors"
                                    >
                                      <Award className="w-3 h-3" />
                                      Google Scholar
                                    </a>
                                  )}
                                  {teacher.semantic_scholar_url && (
                                    <a 
                                      href={teacher.semantic_scholar_url} 
                                      target="_blank" 
                                      rel="noopener noreferrer"
                                      className="px-3 py-1.5 bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 text-xs rounded-lg flex items-center gap-1 hover:bg-purple-100 dark:hover:bg-purple-800/30 transition-colors"
                                    >
                                      <Award className="w-3 h-3" />
                                      Semantic Scholar
                                    </a>
                                  )}
                                  {!teacher.google_scholar_url && !teacher.semantic_scholar_url && (
                                    <span className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-xs rounded-lg">
                                      No academic profiles available
                                    </span>
                                  )}
                                </div>
                              </div>
                              
                              {/* PhD Thesis */}
                              {teacher.phd_thesis && (
                                <div>
                                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">PhD Thesis</h4>
                                  <p className="text-sm text-gray-600 dark:text-gray-400 italic line-clamp-2">
                                    "{teacher.phd_thesis}"
                                  </p>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-10">
                  <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-800 dark:text-white mb-2">
                    No matching professors found
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4 max-w-lg mx-auto">
                    {selectedExpertiseFilter !== 'all' 
                      ? `No professors match the selected expertise filter: "${selectedExpertiseFilter}"`
                      : "We couldn't find any professors with expertise matching your project requirements. Try modifying your project description to be more specific."}
                  </p>
                  {selectedExpertiseFilter !== 'all' && (
                    <button 
                      onClick={() => setSelectedExpertiseFilter('all')}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
                    >
                      Show All Results
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectExpertiseMatcher;