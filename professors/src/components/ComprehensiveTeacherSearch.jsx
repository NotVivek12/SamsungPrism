import React, { useState, useEffect } from 'react';
import { Search, Users, GraduationCap, Mail, ExternalLink, ArrowLeft, Eye, BookOpen, Award, Link as LinkIcon, Calendar, MapPin, Star, TrendingUp, User, Briefcase, FileText, Filter, Grid3X3, List, SortAsc, SortDesc, Heart, Bookmark, Sparkles, Brain } from 'lucide-react';
import aiSearchService from '../services/aiSearchService';

const ComprehensiveTeacherSearch = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isAISearching, setIsAISearching] = useState(false);
  const [aiSearchResult, setAiSearchResult] = useState(null);
  const [showAIHelper, setShowAIHelper] = useState(false);
  const [teachers, setTeachers] = useState([]);
  const [filteredTeachers, setFilteredTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTeacher, setSelectedTeacher] = useState(null);
  const [teacherDetails, setTeacherDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  
  // New UI state
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [sortBy, setSortBy] = useState('name'); // 'name', 'college', 'expertise'
  const [sortOrder, setSortOrder] = useState('asc'); // 'asc' or 'desc'
  const [filterBy, setFilterBy] = useState('all'); // 'all', 'scholar', 'semantic', 'both'
  const [showProfilePicturesOnly, setShowProfilePicturesOnly] = useState(false); // New filter for profile pictures
  const [favoriteTeachers, setFavoriteTeachers] = useState(new Set());

  // Computed variable for teachers with profile pictures
  const teachersWithPictures = teachers.filter(teacher => 
    teacher.profile_picture_url || teacher.scholar_profile_picture
  );

  // Load teachers data from the API
  useEffect(() => {
    const loadTeachers = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch('http://localhost:5000/api/teachers');
        if (response.ok) {
          const data = await response.json();
          console.log('✅ Teachers data loaded:', data.teachers?.length || 0, 'teachers');
          if (data && data.teachers) {
            setTeachers(data.teachers);
            setFilteredTeachers(data.teachers);
            console.log('✅ All 206 teachers displayed in dashboard:', data.teachers.length);
          } else {
            setError('No teachers data available');
            console.error('❌ No teachers data in response');
          }
        } else {
          const errorText = await response.text();
          setError(`Failed to fetch teachers data: ${response.status} ${errorText}`);
          console.error('❌ Failed to fetch teachers, status:', response.status, errorText);
        }
      } catch (err) {
        console.error('Error loading teachers:', err);
        setError('Failed to connect to the server');
      } finally {
        setLoading(false);
      }
    };

    loadTeachers();
  }, []);

  // Handle AI-powered search
  const handleAISearch = async (query) => {
    if (!query || query.trim().length < 3) {
      setAiSearchResult(null);
      return;
    }

    try {
      setIsAISearching(true);
      const aiResult = await aiSearchService.parseSearchQuery(query);
      setAiSearchResult(aiResult);
    } catch (error) {
      console.error('AI search failed:', error);
      setAiSearchResult(null);
    } finally {
      setIsAISearching(false);
    }
  };

  // Enhanced search with AI
  const performSearch = (term) => {
    setSearchTerm(term);
    
    // Trigger AI search for natural language queries
    if (term.length >= 3) {
      // Check if the query is a natural language question
      const isNaturalLanguageQuery = 
        term.includes('expert') || 
        term.includes('good at') || 
        term.includes('skilled') ||
        term.includes('show me') ||
        term.includes('find') ||
        term.includes('who are') ||
        term.includes('professional') ||
        term.includes('specialist') ||
        term.includes('researcher') ||
        term.includes('professor') ||
        term.includes('teacher') ||
        term.split(' ').length > 3; // Multi-word queries are likely natural language
      
      if (isNaturalLanguageQuery) {
        handleAISearch(term);
      } else {
        setAiSearchResult(null);
      }
    } else {
      setAiSearchResult(null);
    }
  };

  // Filter and sort teachers based on search term and filters
  useEffect(() => {
    let filtered = [...teachers];
    
    // AI-powered search when available
    if (searchTerm && aiSearchResult) {
      filtered = aiSearchService.smartSearch(teachers, searchTerm, aiSearchResult);
    } else if (searchTerm) {
      // Fallback to regular search
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(teacher => 
        teacher.name?.toLowerCase().includes(term) ||
        teacher.domain_expertise?.toLowerCase().includes(term) ||
        teacher.college?.toLowerCase().includes(term) ||
        teacher.email?.toLowerCase().includes(term) ||
        teacher.phd_thesis?.toLowerCase().includes(term) ||
        teacher.research_interests?.toLowerCase().includes(term) ||
        teacher.bio?.toLowerCase().includes(term)
      );
    }
    
    // Apply profile filter
    if (filterBy !== 'all') {
      filtered = filtered.filter(teacher => {
        switch (filterBy) {
          case 'scholar':
            return teacher.has_google_scholar && !teacher.has_semantic_scholar;
          case 'semantic':
            return teacher.has_semantic_scholar && !teacher.has_google_scholar;
          case 'both':
            return teacher.has_google_scholar && teacher.has_semantic_scholar;
          case 'none':
            return !teacher.has_google_scholar && !teacher.has_semantic_scholar;
          default:
            return true;
        }
      });
    }
    
    // Apply profile picture filter
    if (showProfilePicturesOnly) {
      filtered = filtered.filter(teacher => 
        teacher.profile_picture_url || teacher.scholar_profile_picture
      );
    }
    
    // Apply sorting
    filtered.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'name':
          aValue = a.name || '';
          bValue = b.name || '';
          break;
        case 'college':
          aValue = a.college || '';
          bValue = b.college || '';
          break;
        case 'expertise':
          aValue = a.domain_expertise || '';
          bValue = b.domain_expertise || '';
          break;
        default:
          aValue = a.name || '';
          bValue = b.name || '';
      }
      
      const comparison = aValue.localeCompare(bValue);
      return sortOrder === 'asc' ? comparison : -comparison;
    });
    
    setFilteredTeachers(filtered);
  }, [searchTerm, teachers, sortBy, sortOrder, filterBy, showProfilePicturesOnly, aiSearchResult]);
  
  // Toggle favorite teacher
  const toggleFavorite = (teacherId) => {
    const newFavorites = new Set(favoriteTeachers);
    if (newFavorites.has(teacherId)) {
      newFavorites.delete(teacherId);
    } else {
      newFavorites.add(teacherId);
    }
    setFavoriteTeachers(newFavorites);
  };
  
  // Sort and filter handlers
  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  // Fetch detailed teacher information including Google Scholar data
  const fetchTeacherDetails = async (teacherId) => {
    try {
      setLoadingDetails(true);
      const response = await fetch(`http://localhost:5000/api/teachers/${teacherId}`);
      if (response.ok) {
        const data = await response.json();
        setTeacherDetails(data);
      } else {
        console.error('Failed to fetch teacher details');
      }
    } catch (err) {
      console.error('Error fetching teacher details:', err);
    } finally {
      setLoadingDetails(false);
    }
  };

  // Handle teacher selection
  const handleTeacherClick = async (teacher) => {
    setSelectedTeacher(teacher);
    await fetchTeacherDetails(teacher.id);
  };

  // Clear search
  const clearSearch = () => {
    setSearchTerm('');
    setAiSearchResult(null);
    setShowAIHelper(false);
  };

  // Comprehensive Profile Page Component
  const TeacherProfilePage = ({ teacher, details, onBack }) => {
    if (!teacher) return null;

    const scholarData = details?.scholar_data;

    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <button
            onClick={onBack}
            className="flex items-center text-blue-600 hover:underline mb-6 font-semibold dark:text-blue-400"
          >
            <ArrowLeft className="w-5 h-5 mr-2" /> Back to Search
          </button>

          {loadingDetails && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-lg text-gray-600">Loading detailed information...</p>
            </div>
          )}

          {details && (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
              {/* Header Section */}
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-12">
                <div className="flex flex-col md:flex-row items-center gap-6">
                  <div className="relative">
                    {/* Display actual profile picture if available */}
                    {(details.profile_picture_url || details.scholar_profile_picture) ? (
                      <div className="w-32 h-32 rounded-full overflow-hidden shadow-xl bg-white p-1">
                        <img
                          src={details.profile_picture_url || details.scholar_profile_picture}
                          alt={`${details.name} profile`}
                          className="w-full h-full object-cover rounded-full"
                          onError={(e) => {
                            // Fallback to initials if image fails to load
                            e.target.style.display = 'none';
                            e.target.nextElementSibling.style.display = 'flex';
                          }}
                        />
                        {/* Fallback initials (hidden by default) */}
                        <div 
                          className="w-full h-full bg-white rounded-full flex items-center justify-center text-4xl font-bold text-blue-600" 
                          style={{ display: 'none' }}
                        >
                          {details.name ? details.name.split(' ').map(n => n[0]).join('').substring(0, 2) : '??'}
                        </div>
                      </div>
                    ) : (
                      // Default avatar with initials when no profile picture
                      <div className="w-32 h-32 bg-white rounded-full flex items-center justify-center text-4xl font-bold text-blue-600 shadow-xl">
                        {details.name ? details.name.split(' ').map(n => n[0]).join('').substring(0, 2) : '??'}
                      </div>
                    )}
                    
                    {/* Picture Source Indicator */}
                    {(details.profile_picture_url || details.scholar_profile_picture) && (
                      <div className="absolute -bottom-2 -right-2 w-8 h-8 rounded-full flex items-center justify-center shadow-lg bg-white">
                        {details.profile_picture_url ? (
                          <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center" title="College Profile Picture">
                            <div className="w-2 h-2 bg-white rounded-full"></div>
                          </div>
                        ) : (
                          <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center" title="Google Scholar Picture">
                            <GraduationCap className="w-3 h-3 text-white" />
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  
                  <div className="text-center md:text-left flex-1">
                    <h1 className="text-4xl font-bold text-white mb-2">{details.name}</h1>
                    <p className="text-xl text-blue-100 mb-2">{details.college}</p>
                    <p className="text-blue-200">{details.email}</p>
                    
                    {/* Academic Achievement Summary */}
                    {details.academic_data?.has_academic_data && (
                      <div className="flex flex-wrap gap-4 mt-4">
                        {details.academic_data.citations > 0 && (
                          <div className="bg-white/20 text-white px-4 py-2 rounded-lg">
                            <span className="font-bold">{details.academic_data.citations}</span> Citations
                          </div>
                        )}
                        {details.academic_data.h_index > 0 && (
                          <div className="bg-white/20 text-white px-4 py-2 rounded-lg">
                            <span className="font-bold">{details.academic_data.h_index}</span> h-index
                          </div>
                        )}
                        {details.academic_data.total_publications > 0 && (
                          <div className="bg-white/20 text-white px-4 py-2 rounded-lg">
                            <span className="font-bold">{details.academic_data.total_publications}</span> Publications
                          </div>
                        )}
                      </div>
                    )}
                    
                    {/* Data Sources */}
                    {details.academic_data?.data_sources && details.academic_data.data_sources.length > 0 && (
                      <div className="mt-3">
                        <p className="text-sm text-blue-200">
                          Academic data from: {details.academic_data.data_sources.join(', ')}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="p-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  {/* Left Column - Basic Information */}
                  <div className="lg:col-span-2 space-y-8">
                    {/* Research Domain */}
                    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                      <h2 className="text-2xl font-semibold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                        <Briefcase className="w-6 h-6" />
                        Research Domain & Expertise
                      </h2>
                      <div className="flex flex-wrap gap-2">
                        {details.research_domains?.map((domain, index) => (
                          <span
                            key={index}
                            className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm"
                          >
                            {domain}
                          </span>
                        )) || details.domain_expertise?.split(',').map((domain, index) => (
                          <span
                            key={index}
                            className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm"
                          >
                            {domain.trim()}
                          </span>
                        ))}
                      </div>
                      
                      {/* Academic Research Interests from Scholar Data */}
                      {details.academic_data?.research_interests && details.academic_data.research_interests.length > 0 && (
                        <div className="mt-4">
                          <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">Academic Research Interests:</h3>
                          <div className="flex flex-wrap gap-2">
                            {details.academic_data.research_interests.map((interest, index) => (
                              <span
                                key={index}
                                className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full text-xs"
                              >
                                {interest}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* PhD Thesis */}
                    {details.phd_thesis && (
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                        <h2 className="text-2xl font-semibold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                          <FileText className="w-6 h-6" />
                          PhD Thesis
                        </h2>
                        <p className="text-gray-700 dark:text-gray-300 italic">
                          "{details.phd_thesis}"
                        </p>
                      </div>
                    )}

                    {/* Academic Metrics and Publications */}
                    {details.academic_data?.has_academic_data && (
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                        <h2 className="text-2xl font-semibold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                          <Award className="w-6 h-6" />
                          Academic Metrics & Publications
                        </h2>
                        
                        {/* Citation Metrics */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                          <div className="text-center p-4 bg-white dark:bg-gray-600 rounded-lg">
                            <div className="text-2xl font-bold text-blue-600">{details.academic_data.citations || 0}</div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">Citations</div>
                          </div>
                          <div className="text-center p-4 bg-white dark:bg-gray-600 rounded-lg">
                            <div className="text-2xl font-bold text-green-600">{details.academic_data.h_index || 0}</div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">h-index</div>
                          </div>
                          {details.academic_data.i10_index > 0 && (
                            <div className="text-center p-4 bg-white dark:bg-gray-600 rounded-lg">
                              <div className="text-2xl font-bold text-purple-600">{details.academic_data.i10_index}</div>
                              <div className="text-sm text-gray-600 dark:text-gray-400">i10-index</div>
                            </div>
                          )}
                          <div className="text-center p-4 bg-white dark:bg-gray-600 rounded-lg">
                            <div className="text-2xl font-bold text-orange-600">{details.academic_data.total_publications || 0}</div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">Publications</div>
                          </div>
                        </div>

                        {/* Recent Publications */}
                        {details.academic_data.recent_publications && details.academic_data.recent_publications.length > 0 && (
                          <div>
                            <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-3">Recent Publications</h3>
                            <div className="space-y-3 max-h-64 overflow-y-auto">
                              {details.academic_data.recent_publications.map((pub, index) => (
                                <div key={index} className="p-3 bg-white dark:bg-gray-600 rounded border-l-4 border-blue-500">
                                  <h4 className="font-medium text-gray-800 dark:text-white">{pub.title}</h4>
                                  {pub.authors && <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{pub.authors}</p>}
                                  {pub.venue && <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">{pub.venue}</p>}
                                  <div className="flex items-center gap-4 mt-2">
                                    {pub.year && <span className="text-xs text-gray-400 dark:text-gray-400">Year: {pub.year}</span>}
                                    {pub.citations && <span className="text-xs text-blue-600 dark:text-blue-400">Citations: {pub.citations}</span>}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Data Source Attribution */}
                        {details.academic_data.data_sources && details.academic_data.data_sources.length > 0 && (
                          <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded">
                            <p className="text-sm text-blue-700 dark:text-blue-300">
                              📊 Academic data extracted from: {details.academic_data.data_sources.join(', ')}
                            </p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Right Column - Additional Info */}
                  <div className="space-y-6">
                    {/* Contact Information */}
                    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                        <Mail className="w-5 h-5" />
                        Contact Information
                      </h3>
                      <div className="space-y-3">
                        <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                          <MapPin className="w-4 h-4" />
                          <span className="text-sm">{details.college}</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                          <Mail className="w-4 h-4" />
                          <span className="text-sm">{details.email}</span>
                        </div>
                        {details.timestamp && (
                          <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                            <Calendar className="w-4 h-4" />
                            <span className="text-sm">Updated: {new Date(details.timestamp).toLocaleDateString()}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Research Interests (from domain expertise) */}
                    {details.domain_expertise && (
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                        <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                          <Star className="w-5 h-5" />
                          Research Areas
                        </h3>
                        <div className="space-y-2">
                          {details.domain_expertise.split(',').map((area, index) => (
                            <div key={index} className="flex items-center gap-2">
                              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                              <span className="text-sm text-gray-700 dark:text-gray-300">{area.trim()}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Scholar Profile Stats */}
                    {scholarData && scholarData.profile_info && (
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                        <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                          <TrendingUp className="w-5 h-5" />
                          Profile Information
                        </h3>
                        <div className="space-y-2 text-sm">
                          {scholarData.profile_info.affiliation && (
                            <p className="text-gray-700 dark:text-gray-300">
                              <span className="font-medium">Affiliation:</span> {scholarData.profile_info.affiliation}
                            </p>
                          )}
                          {scholarData.profile_info.interests && (
                            <div>
                              <span className="font-medium text-gray-700 dark:text-gray-300">Interests:</span>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {scholarData.profile_info.interests.map((interest, index) => (
                                  <span key={index} className="px-2 py-1 bg-blue-100 dark:blue-900 text-blue-800 dark:text-blue-200 text-xs rounded">
                                    {interest}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  // Show profile page if teacher is selected
  if (selectedTeacher) {
    return (
      <TeacherProfilePage 
        teacher={selectedTeacher} 
        details={teacherDetails}
        onBack={() => {
          setSelectedTeacher(null);
          setTeacherDetails(null);
        }} 
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-cyan-500 font-sans tracking-tight mb-4">
            🤖 AI-Powered Faculty Research Directory
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            Find experts using natural language search - "Show me professors good at artificial intelligence"
          </p>
        </div>

        {/* Search and Controls Section */} 
        <div className="mb-8 space-y-4">
          {/* Search Bar */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-6 h-6" />
              {isAISearching && (
                <Brain className="absolute left-12 top-1/2 transform -translate-y-1/2 text-blue-500 w-5 h-5 animate-pulse" />
              )}
              <input
                type="text"
                placeholder="🤖 AI-Powered Search: Try 'Show me experts in artificial intelligence' or 'Find professors good at machine learning'..."
                value={searchTerm}
                onChange={(e) => performSearch(e.target.value)}
                className="w-full p-4 pl-12 pr-16 text-lg border border-gray-300 dark:border-gray-600 rounded-full 
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                           focus:ring-2 focus:ring-blue-500 focus:border-transparent 
                           transition duration-300 shadow-lg"
              />
              <div className="absolute right-4 top-1/2 transform -translate-y-1/2 flex items-center gap-2">
                {aiSearchResult && (
                  <button
                    onClick={() => setShowAIHelper(!showAIHelper)}
                    className="p-1 rounded-full bg-blue-100 text-blue-600 hover:bg-blue-200 transition-colors"
                    title="AI Search Details"
                  >
                    <Sparkles className="w-4 h-4" />
                  </button>
                )}
                {searchTerm && (
                  <button
                    onClick={clearSearch}
                    className="text-gray-400 hover:text-gray-600 text-xl"
                  >
                    ×
                  </button>
                )}
              </div>
            </div>
            
            {/* AI Search Result Info */}
            {aiSearchResult && showAIHelper && (
              <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
                <div className="flex items-center gap-2 mb-2">
                  <Brain className="w-4 h-4 text-blue-600" />
                  <span className="text-sm font-semibold text-blue-800 dark:text-blue-200">AI Search Understanding</span>
                </div>
                <p className="text-sm text-blue-700 dark:text-blue-300 mb-2">{aiSearchResult.intent}</p>
                {aiSearchResult.keywords && aiSearchResult.keywords.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    <span className="text-xs text-blue-600 dark:text-blue-400">Keywords:</span>
                    {aiSearchResult.keywords.slice(0, 6).map((keyword, index) => (
                      <span key={index} className="px-2 py-1 bg-blue-100 dark:blue-800 text-blue-800 dark:text-blue-200 text-xs rounded-full">
                        {keyword}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}
            
            {/* AI Search Suggestions */}
            {!searchTerm && (
              <div className="mt-4">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">💡 Try AI-powered natural language search:</p>
                <div className="flex flex-wrap gap-2">
                  {[
                    "Show me experts in artificial intelligence",
                    "Find professors good at machine learning", 
                    "Who are skilled in data science?",
                    "Computer vision researchers",
                    "Cybersecurity specialists",
                    "Who are expert in artificial intelligence?",
                    "Show me teachers very professional in AI"
                  ].map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => performSearch(suggestion)}
                      className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-full hover:bg-blue-100 dark:hover:bg-blue-900 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Controls Row */}
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
            {/* Left side - Filters and Sort */}
            <div className="flex flex-col sm:flex-row flex-wrap items-start sm:items-center gap-3 order-2 lg:order-1">
              {/* Filter Dropdown */}
              <div className="relative w-full sm:w-auto">
                <select
                  value={filterBy}
                  onChange={(e) => setFilterBy(e.target.value)}
                  className="w-full sm:w-auto appearance-none bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 pr-8 text-sm font-medium text-gray-700 dark:text-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-sm"
                >
                  <option value="all">All Profiles</option>
                  <option value="scholar">Google Scholar Only</option>
                  <option value="semantic">Semantic Scholar Only</option>
                  <option value="both">Both Profiles</option>
                  <option value="none">No Profiles</option>
                </select>
                <Filter className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>

              {/* Sort Options */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 w-full sm:w-auto">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">Sort by:</span>
                <div className="flex gap-2 w-full sm:w-auto">
                  <button
                    onClick={() => handleSort('name')}
                    className={`flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm flex-1 sm:flex-none justify-center ${
                      sortBy === 'name' 
                        ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300' 
                        : 'bg-white text-gray-600 hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700'
                    }`}
                  >
                    Name
                    {sortBy === 'name' && (sortOrder === 'asc' ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />)}
                  </button>
                  <button
                    onClick={() => handleSort('college')}
                    className={`flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm flex-1 sm:flex-none justify-center ${
                      sortBy === 'college' 
                        ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300' 
                        : 'bg-white text-gray-600 hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700'
                    }`}
                  >
                    College
                    {sortBy === 'college' && (sortOrder === 'asc' ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />)}
                  </button>
                </div>
              </div>
            </div>

            {/* Right side - View Mode and Results Count */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between sm:justify-end gap-4 w-full lg:w-auto order-1 lg:order-2">
              {/* Results Count */}
              <span className="text-sm text-gray-600 dark:text-gray-400 font-medium order-2 sm:order-1">
                {loading ? 'Loading...' : 
                 `${filteredTeachers.length} teacher${filteredTeachers.length !== 1 ? 's' : ''} ${searchTerm ? 'found' : 'in database'}`}
              </span>

              {/* View Mode Toggle */}
              <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1 shadow-sm w-full sm:w-auto order-1 sm:order-2">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors flex-1 sm:flex-none justify-center ${
                    viewMode === 'grid'
                      ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
                  }`}
                >
                  <Grid3X3 className="w-4 h-4" />
                  <span>Grid</span>
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={viewMode === 'list'
                    ? "flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors flex-1 sm:flex-none justify-center bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm"
                    : "flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors flex-1 sm:flex-none justify-center text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"}
                >
                  <List className="w-4 h-4" />
                  <span>List</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Main content area */}
        <div>
          {/* Error Message */}
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="text-center py-10">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-lg text-gray-600">Loading faculty directory...</p>
            </div>
          )}

          {/* Teachers Display */}
          {!loading && (
            <>
              {/* Grid View */}
              {viewMode === 'grid' && (
                <div className="w-full max-w-7xl mx-auto grid gap-6 sm:gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4">
                  {filteredTeachers.length > 0 ? (
                    filteredTeachers.map(teacher => (
                      <div key={teacher.id} className="group relative bg-white rounded-3xl shadow-lg hover:shadow-2xl transform hover:-translate-y-2 transition-all duration-500 border border-gray-100 overflow-hidden dark:bg-gray-800 dark:border-gray-700">
                        {/* Card Header with Gradient Background */}
                        <div className="relative p-6 pb-4 bg-gradient-to-br from-indigo-50 via-blue-50 to-cyan-50 dark:from-gray-700 dark:via-gray-800 dark:to-gray-900">
                          <div className="absolute top-4 right-4 flex gap-2">
                            {/* Favorite Button */}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleFavorite(teacher.id);
                              }}
                              className={`p-2 rounded-full transition-all duration-300 ${
                                favoriteTeachers.has(teacher.id)
                                  ? 'bg-red-100 text-red-600 hover:bg-red-200'
                                  : 'bg-gray-100 text-gray-400 hover:bg-gray-200 hover:text-red-500'
                              }`}
                            >
                              <Heart className={`w-4 h-4 ${favoriteTeachers.has(teacher.id) ? 'fill-current' : ''}`} />
                            </button>
                            
                            {/* Scholar Status Indicators */}
                            {teacher.has_google_scholar && (
                              <div className="w-3 h-3 bg-green-500 rounded-full shadow-lg animate-pulse" title="Google Scholar Profile"></div>
                            )}
                            {teacher.has_semantic_scholar && (
                              <div className="w-3 h-3 bg-purple-500 rounded-full shadow-lg animate-pulse" title="Semantic Scholar Profile"></div>
                            )}
                          </div>
                          
                          {/* Avatar and Basic Info with Profile Pictures */}
                          <div className="flex items-start gap-4">
                            <div className="relative">
                              {/* Display actual profile picture if available */}
                              {(teacher.profile_picture_url || teacher.scholar_profile_picture) ? (
                                <div className="w-16 h-16 rounded-2xl overflow-hidden shadow-lg bg-gray-200 dark:bg-gray-600">
                                  <img
                                    src={teacher.profile_picture_url || teacher.scholar_profile_picture}
                                    alt={`${teacher.name} profile`}
                                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                                    onError={(e) => {
                                      // Fallback to initials if image fails to load
                                      e.target.style.display = 'none';
                                      e.target.nextElementSibling.style.display = 'flex';
                                    }}
                                  />
                                  {/* Fallback initials (hidden by default) */}
                                  <div 
                                    className="w-full h-full bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-600 rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-lg" 
                                    style={{ display: 'none' }}
                                  >
                                    {teacher.name ? teacher.name.split(' ').map(n => n[0]).join('').substring(0, 2) : '??'}
                                  </div>
                                </div>
                              ) : (
                                // Default avatar with initials when no profile picture
                                <div className="w-16 h-16 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-600 rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-lg">
                                  {teacher.name ? teacher.name.split(' ').map(n => n[0]).join('').substring(0, 2) : '??'}
                                </div>
                              )}
                              
                              {/* Profile indicator badge */}
                              <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-white rounded-full flex items-center justify-center shadow-md dark:bg-gray-800">
                                {(teacher.profile_picture_url || teacher.scholar_profile_picture) ? (
                                  <div className="w-3 h-3 bg-green-500 rounded-full" title="Has Profile Picture" />
                                ) : (
                                  <User className="w-3 h-3 text-gray-600 dark:text-gray-300" />
                                )}
                              </div>
                            </div>
                            
                            <div className="flex-1 min-w-0">
                              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1 truncate group-hover:text-blue-600 transition-colors duration-300">
                                {teacher.name}
                              </h3>
                              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
                                <MapPin className="w-4 h-4 flex-shrink-0" />
                                <span className="truncate">{teacher.college}</span>
                              </div>
                              {teacher.email && (
                                <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-500">
                                  <Mail className="w-4 h-4 flex-shrink-0" />
                                  <span className="truncate">{teacher.email}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Card Body */}
                        <div className="p-6 pt-4">
                          {/* Research Areas */}
                          <div className="mb-5">
                            <div className="flex items-center gap-2 mb-3">
                              <Briefcase className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Research Areas</span>
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {teacher.domain_expertise?.split(',').slice(0, 3).map((domain, index) => (
                                <span 
                                  key={index} 
                                  className="px-3 py-1.5 bg-gradient-to-r from-blue-500 to-cyan-500 text-white text-xs font-medium rounded-full shadow-sm hover:shadow-md transition-shadow duration-300"
                                >
                                  {domain.trim()}
                                </span>
                              ))}
                              {teacher.domain_expertise?.split(',').length > 3 && (
                                <span className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs font-medium rounded-full border border-gray-200 dark:border-gray-600">
                                  +{teacher.domain_expertise.split(',').length - 3} more
                                </span>
                              )}
                            </div>
                          </div>

                          {/* Academic Profiles Links */}
                          {(teacher.google_scholar_url || teacher.semantic_scholar_url || teacher.profile_link) && (
                            <div className="mb-5">
                              <div className="flex items-center gap-2 mb-3">
                                <LinkIcon className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                                <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Academic Links</span>
                              </div>
                              <div className="flex flex-wrap gap-2">
                                {teacher.google_scholar_url && (
                                  <a 
                                    href={teacher.google_scholar_url} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="px-3 py-1.5 bg-green-50 border border-green-200 text-green-700 text-xs rounded-lg flex items-center gap-1 hover:bg-green-100 transition-colors"
                                  >
                                    <GraduationCap className="w-3 h-3" />
                                    Google Scholar
                                  </a>
                                )}
                                {teacher.semantic_scholar_url && (
                                  <a 
                                    href={teacher.semantic_scholar_url} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="px-3 py-1.5 bg-purple-50 border border-purple-200 text-purple-700 text-xs rounded-lg flex items-center gap-1 hover:bg-purple-100 transition-colors"
                                  >
                                    <BookOpen className="w-3 h-3" />
                                    Semantic Scholar
                                  </a>
                                )}
                                {teacher.profile_link && (
                                  <a 
                                    href={teacher.profile_link} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="px-3 py-1.5 bg-blue-50 border border-blue-200 text-blue-700 text-xs rounded-lg flex items-center gap-1 hover:bg-blue-100 transition-colors"
                                  >
                                    <User className="w-3 h-3" />
                                    Profile
                                  </a>
                                )}
                              </div>
                            </div>
                          )}

                          {/* Academic Status */}
                          <div className="mb-5">
                            <div className="flex items-center gap-3">
                              <div className="flex items-center gap-2">
                                <Award className="w-4 h-4 text-yellow-500" />
                                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Academic Profiles</span>
                              </div>
                              <div className="flex gap-2">
                                {teacher.has_google_scholar && (
                                  <span className="px-2 py-1 bg-green-50 border border-green-200 text-green-700 text-xs rounded-lg flex items-center gap-1">
                                    <GraduationCap className="w-3 h-3" />
                                    Scholar
                                  </span>
                                )}
                                {teacher.has_semantic_scholar && (
                                  <span className="px-2 py-1 bg-purple-50 border border-purple-200 text-purple-700 text-xs rounded-lg flex items-center gap-1">
                                    <BookOpen className="w-3 h-3" />
                                    Semantic
                                  </span>
                                )}
                                {!teacher.has_google_scholar && !teacher.has_semantic_scholar && (
                                  <span className="px-2 py-1 bg-gray-50 border border-gray-200 text-gray-500 text-xs rounded-lg">
                                    No profiles
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>

                          {/* Action Button */}
                          <button
                            onClick={() => handleTeacherClick(teacher)}
                            className="w-full py-3 px-4 text-white font-semibold rounded-2xl shadow-lg bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 hover:from-blue-700 hover:via-purple-700 hover:to-indigo-700 transform hover:scale-105 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 flex items-center justify-center gap-3 group-hover:shadow-xl"
                          >
                            <Eye className="w-5 h-5 transform group-hover:scale-110 transition-transform duration-300" />
                            <span>View Full Profile</span>
                            <ExternalLink className="w-4 h-4 opacity-70" />
                          </button>
                        </div>

                        {/* Hover Effect Overlay */}
                        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 to-purple-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none rounded-3xl"></div>
                      </div>
                    ))
                  ) : (
                    <div className="col-span-full text-center py-12">
                      <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                        No teachers found
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400 mb-4">
                        {searchTerm ? `No teachers found matching "${searchTerm}". Try a different search term.` : 'No teachers match the selected filters.'}
                      </p>
                      {searchTerm && (
                        <button
                          onClick={clearSearch}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
                        >
                          Clear Search
                        </button>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* List View */}
              {viewMode === 'list' && (
                <div className="w-full max-w-7xl mx-auto space-y-4">
                  {filteredTeachers.length > 0 ? (
                    filteredTeachers.map(teacher => (
                      <div key={teacher.id} className="group bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 border border-gray-100 overflow-hidden dark:bg-gray-800 dark:border-gray-700">
                        <div className="flex items-center p-6 gap-6">
                          {/* Avatar */}
                          <div className="relative flex-shrink-0">
                            <div className="w-16 h-16 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-600 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-lg">
                              {teacher.name ? teacher.name.split(' ').map(n => n[0]).join('').substring(0, 2) : '??'}
                            </div>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleFavorite(teacher.id);
                              }}
                              className={`absolute -top-2 -right-2 p-1.5 rounded-full transition-all duration-300 ${
                                favoriteTeachers.has(teacher.id)
                                  ? 'bg-red-100 text-red-600 hover:bg-red-200'
                                  : 'bg-gray-100 text-gray-400 hover:bg-gray-200 hover:text-red-500'
                              }`}
                            >
                              <Heart className={`w-3 h-3 ${favoriteTeachers.has(teacher.id) ? 'fill-current' : ''}`} />
                            </button>
                          </div>

                          {/* Main Info */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1 min-w-0">
                                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1 group-hover:text-blue-600 transition-colors duration-300">
                                  {teacher.name}
                                </h3>
                                <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
                                  <div className="flex items-center gap-1">
                                    <MapPin className="w-4 h-4" />
                                    <span>{teacher.college}</span>
                                  </div>
                                  {teacher.email && (
                                    <div className="flex items-center gap-1">
                                      <Mail className="w-4 h-4" />
                                      <span className="truncate">{teacher.email}</span>
                                    </div>
                                  )}
                                </div>
                                
                                {/* Research Areas */}
                                <div className="flex flex-wrap gap-2 mb-3">
                                  {teacher.domain_expertise?.split(',').slice(0, 4).map((domain, index) => (
                                    <span 
                                      key={index} 
                                      className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-full"
                                    >
                                      {domain.trim()}
                                    </span>
                                  ))}
                                  {teacher.domain_expertise?.split(',').length > 4 && (
                                    <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded-full">
                                      +{teacher.domain_expertise.split(',').length - 4} more
                                    </span>
                                  )}
                                </div>

                                {/* PhD Thesis (if available) */}
                                {teacher.phd_thesis && (
                                  <div className="mb-3">
                                    <div className="flex items-center gap-2 mb-1">
                                      <FileText className="w-3 h-3 text-gray-500" />
                                      <span className="text-xs font-medium text-gray-600 dark:text-gray-400">PhD Thesis</span>
                                    </div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                                      {teacher.phd_thesis}
                                    </p>
                                  </div>
                                )}

                                {/* Academic Links */}
                                <div className="flex items-center gap-3">
                                  <div className="flex items-center gap-2">
                                    <Award className="w-4 h-4 text-yellow-500" />
                                    <span className="text-xs font-medium text-gray-600 dark:text-gray-400">Profiles:</span>
                                  </div>
                                  <div className="flex gap-2">
                                    {teacher.google_scholar_url && (
                                      <a 
                                        href={teacher.google_scholar_url} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="px-2 py-1 bg-green-50 border border-green-200 text-green-700 text-xs rounded flex items-center gap-1 hover:bg-green-100 transition-colors"
                                        onClick={(e) => e.stopPropagation()}
                                      >
                                        <GraduationCap className="w-3 h-3" />
                                        Scholar
                                      </a>
                                    )}
                                    {teacher.semantic_scholar_url && (
                                      <a 
                                        href={teacher.semantic_scholar_url} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="px-2 py-1 bg-purple-50 border border-purple-200 text-purple-700 text-xs rounded flex items-center gap-1 hover:bg-purple-100 transition-colors"
                                        onClick={(e) => e.stopPropagation()}
                                      >
                                        <BookOpen className="w-3 h-3" />
                                        Semantic
                                      </a>
                                    )}
                                    {teacher.profile_link && (
                                      <a 
                                        href={teacher.profile_link} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="px-2 py-1 bg-blue-50 border border-blue-200 text-blue-700 text-xs rounded flex items-center gap-1 hover:bg-blue-100 transition-colors"
                                        onClick={(e) => e.stopPropagation()}
                                      >
                                        <User className="w-3 h-3" />
                                        Profile
                                      </a>
                                    )}
                                    {!teacher.google_scholar_url && !teacher.semantic_scholar_url && !teacher.profile_link && (
                                      <span className="px-2 py-1 bg-gray-50 border border-gray-200 text-gray-500 text-xs rounded">
                                        No profiles
                                      </span>
                                    )}
                                  </div>
                                </div>
                              </div>

                              {/* Status Indicators & Actions */}
                              <div className="flex-shrink-0 flex items-center gap-3">
                                {/* Academic Status Indicators */}
                                <div className="flex gap-1">
                                  {teacher.has_google_scholar && (
                                    <div className="w-3 h-3 bg-green-500 rounded-full shadow-lg animate-pulse" title="Google Scholar Profile"></div>
                                  )}
                                  {teacher.has_semantic_scholar && (
                                    <div className="w-3 h-3 bg-purple-500 rounded-full shadow-lg animate-pulse" title="Semantic Scholar Profile"></div>
                                  )}
                                </div>

                                {/* Database Info */}
                                {teacher.row_number && (
                                  <div className="text-xs text-gray-400 dark:text-gray-500">
                                    #{teacher.row_number}
                                  </div>
                                )}

                                {/* View Profile Button */}
                                <button
                                  onClick={() => handleTeacherClick(teacher)}
                                  className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm font-medium rounded-lg hover:from-blue-700 hover:to-purple-700 transform hover:scale-105 transition-all duration-300 flex items-center gap-2"
                                >
                                  <Eye className="w-4 h-4" />
                                  View Profile
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="col-span-full text-center py-12">
                      {(!searchTerm && filterBy === 'all') ? (
                        <div>
                          <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                            Welcome to Faculty Research Directory
                          </h3>
                          <p className="text-gray-600 dark:text-gray-400 mb-4">
                            Search our comprehensive database of 206+ faculty members to discover their research profiles, PhD thesis topics, academic affiliations, and publication data.
                          </p>
                          <div className="flex flex-wrap justify-center gap-2 text-sm text-gray-500">
                            <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">Try: "Machine Learning"</span>
                            <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">Try: "Computer Science"</span>
                            <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">Try: "Data Science"</span>
                            <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">Try: "AI"</span>
                          </div>
                        </div>
                      ) : (
                        <div>
                          <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                            No teachers found
                          </h3>
                          <p className="text-gray-600 dark:text-gray-400 mb-4">
                            {searchTerm ? `No teachers found matching "${searchTerm}". Try a different search term.` : 'No teachers match the selected filters.'}
                          </p>
                          {searchTerm && (
                            <button
                              onClick={clearSearch}
                              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
                            >
                              Clear Search
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ComprehensiveTeacherSearch;