import React, { useState, useEffect } from 'react';
import { Search, Users, GraduationCap, Mail, ExternalLink, ArrowLeft, Eye, BookOpen, Award, Calendar, MapPin, Star, TrendingUp, User, Briefcase, FileText, Filter, Grid3X3, List, SortAsc, SortDesc, Heart, Download } from 'lucide-react';

const ComprehensiveTeacherSearch = () => {
  // Add global styles for scrollable content
  useEffect(() => {
    const styleEl = document.createElement('style');
    styleEl.textContent = `
      /* Set max-height for card content */
      .card-content-scrollable {
        max-height: 300px;
        overflow-y: auto;
      }
      
      /* Custom scrollbar styling */
      .card-content-scrollable::-webkit-scrollbar {
        width: 4px;
      }
      .card-content-scrollable::-webkit-scrollbar-track {
        background: #f1f5f9;
      }
      .card-content-scrollable::-webkit-scrollbar-thumb {
        background-color: #cbd5e1;
        border-radius: 20px;
      }
      .dark .card-content-scrollable::-webkit-scrollbar-track {
        background: #1e293b;
      }
      .dark .card-content-scrollable::-webkit-scrollbar-thumb {
        background-color: #475569;
      }
    `;
    document.head.appendChild(styleEl);
    
    return () => {
      document.head.removeChild(styleEl);
    };
  }, []);
  const [searchTerm, setSearchTerm] = useState('');
  const [, setIsAISearching] = useState(false);
  const [aiServerResults, setAiServerResults] = useState(null);
  const [teachers, setTeachers] = useState([]);
  const [filteredTeachers, setFilteredTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTeacher, setSelectedTeacher] = useState(null);
  const [teacherDetails, setTeacherDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  
  // New UI state
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [sortBy, setSortBy] = useState('name'); // 'name', 'college', 'expertise', 'citations'
  const [sortOrder, setSortOrder] = useState('asc'); // 'asc' or 'desc' - for citations, 'asc' means highest first
  const [filterBy, setFilterBy] = useState('all'); // 'all', 'scholar', 'semantic', 'both', 'none', or college name
  const [showProfilePicturesOnly] = useState(false); // New filter for profile pictures
  const [favoriteTeachers, setFavoriteTeachers] = useState(new Set());
  
  // College filter state (simplified since it's now part of filterBy)
  const [availableColleges, setAvailableColleges] = useState([]);

  // Computed variable for teachers with profile pictures
  // eslint-disable-next-line no-unused-vars
  const teachersWithPictures = teachers.filter(teacher => 
    teacher.profile_picture_url || teacher.scholar_profile_picture
  );

  // Load teachers data from the API
  useEffect(() => {
    const loadTeachers = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Include citation data in the API request
        const response = await fetch('http://localhost:5000/api/professors?include_citations=true');
        if (response.ok) {
          const data = await response.json();
          console.log('✅ Professors data loaded:', data.professors?.length || 0, 'professors');
          if (data && data.professors) {
            setTeachers(data.professors);
            setFilteredTeachers(data.professors);
            
            // Check for citation data
            const professorsWithCitations = data.professors.filter(p => 
              p.citations_count > 0 || p.h_index > 0 || p.i10_index > 0
            );
            console.log(`✅ Professors with citation data: ${professorsWithCitations.length}/${data.professors.length}`);
            
            // Extract unique colleges for filter dropdown (normalize case to avoid duplicates)
            const collegeSet = new Set();
            data.professors.forEach(teacher => {
              if (teacher.college && teacher.college.trim()) {
                // Normalize college name: trim whitespace and convert to title case
                const normalizedCollege = teacher.college.trim()
                  .toLowerCase()
                  .split(' ')
                  .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                  .join(' ');
                collegeSet.add(normalizedCollege);
              }
            });
            const colleges = Array.from(collegeSet).sort();
            setAvailableColleges(colleges);
            
            console.log('✅ All professors displayed in dashboard:', data.professors.length);
            console.log('✅ Extracted unique colleges:', colleges.length);
          } else {
            setError('No professors data available');
            console.error('❌ No professors data in response');
          }
        } else {
          const errorText = await response.text();
          setError(`Failed to fetch professors data: ${response.status} ${errorText}`);
          console.error('❌ Failed to fetch professors, status:', response.status, errorText);
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

  // Debounced server-side AI search while typing
  useEffect(() => {
    const q = searchTerm?.trim() || '';
    // Trigger for 2+ chars to allow short skills like "AI"
    if (q.length < 2) {
      setAiServerResults(null);
      setIsAISearching(false);
      return;
    }

    const controller = new AbortController();
    setIsAISearching(true);
    const timer = setTimeout(async () => {
      try {
        const resp = await fetch((process.env.REACT_APP_API_BASE || 'http://localhost:5000') + '/api/ai/search-teachers', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: q }),
          signal: controller.signal
        });
        if (resp.ok) {
          const data = await resp.json();
          setAiServerResults(Array.isArray(data.professors) ? data.professors : []);
        } else {
          setAiServerResults(null);
        }
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('AI search failed:', err);
          setAiServerResults(null);
        }
      } finally {
        setIsAISearching(false);
      }
    }, 350);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [searchTerm]);

  // Filter and sort teachers based on search term and filters
  useEffect(() => {
    // Prefer server-side AI results when available; else use full teachers list
    let baseList = aiServerResults && Array.isArray(aiServerResults) ? [...aiServerResults] : [...teachers];
    let filtered = baseList;

    // Fallback to regular search when no server results
    if (searchTerm && (!aiServerResults || aiServerResults.length === 0)) {
      const term = searchTerm.toLowerCase();
      filtered = baseList.filter(teacher =>
        teacher.name?.toLowerCase().includes(term) ||
        teacher.domain_expertise?.toLowerCase().includes(term) ||
        teacher.college?.toLowerCase().includes(term) ||
        teacher.email?.toLowerCase().includes(term) ||
        teacher.phd_thesis?.toLowerCase().includes(term) ||
        teacher.research_interests?.toLowerCase().includes(term) ||
        teacher.bio?.toLowerCase().includes(term)
      );
    }
    
    // Apply filter
    if (filterBy !== 'all') {
      // Handle college filter (filterBy is a college name)
      filtered = filtered.filter(teacher => {
        if (!teacher.college) return false;
        // Normalize the teacher's college name to match our normalized list
        const normalizedTeacherCollege = teacher.college.trim()
          .toLowerCase()
          .split(' ')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');
        return normalizedTeacherCollege === filterBy;
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
          return sortOrder === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
        case 'college':
          aValue = a.college || '';
          bValue = b.college || '';
          return sortOrder === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
        case 'expertise':
          aValue = a.domain_expertise || '';
          bValue = b.domain_expertise || '';
          return sortOrder === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
        case 'citations':
          // Use numerical sorting for citations, treating undefined/null as 0
          aValue = a.citations_count || 0;
          bValue = b.citations_count || 0;
          // For citations, default to showing highest citations first when 'asc' is selected
          // (contrary to usual sorting behavior, but more intuitive for citations)
          return sortOrder === 'asc' ? bValue - aValue : aValue - bValue;
        default:
          aValue = a.name || '';
          bValue = b.name || '';
          return sortOrder === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
      }
    });
    
    setFilteredTeachers(filtered);
  }, [searchTerm, teachers, sortBy, sortOrder, filterBy, showProfilePicturesOnly, aiServerResults]);
  
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

  // Export functionality
  const handleExport = () => {
    try {
      // Prepare CSV data
      const csvHeaders = [
        'Name',
        'College',
        'Email',
        'Domain Expertise',
        'Citations Count',
        'H-Index',
        'I10-Index',
        'PhD Thesis',
        'Google Scholar URL',
        'Semantic Scholar URL',
        'Profile Link'
      ];

      // Convert filtered teachers data to CSV rows
      const csvRows = filteredTeachers.map(teacher => [
        `"${(teacher.name || '').replace(/"/g, '""')}"`,
        `"${(teacher.college || '').replace(/"/g, '""')}"`,
        `"${(teacher.email || '').replace(/"/g, '""')}"`,
        `"${(teacher.domain_expertise || '').replace(/"/g, '""')}"`,
        teacher.citations_count || 0,
        teacher.h_index || 0,
        teacher.i10_index || 0,
        `"${(teacher.phd_thesis || '').replace(/"/g, '""')}"`,
        `"${(teacher.google_scholar_url || '').replace(/"/g, '""')}"`,
        `"${(teacher.semantic_scholar_url || '').replace(/"/g, '""')}"`,
        `"${(teacher.profile_link || '').replace(/"/g, '""')}"`
      ]);

      // Combine headers and rows
      const csvContent = [csvHeaders.join(','), ...csvRows.map(row => row.join(','))].join('\n');

      // Create and download the file
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      
      if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        
        // Generate filename with current date and filter info
        const currentDate = new Date().toISOString().split('T')[0];
        const filterInfo = filterBy !== 'all' ? `_${filterBy.replace(/\s+/g, '_')}` : '';
        const searchInfo = searchTerm ? `_search_${searchTerm.replace(/[^a-zA-Z0-9]/g, '_')}` : '';
        const filename = `professors_export_${currentDate}${filterInfo}${searchInfo}.csv`;
        
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Show success message (you can replace this with a toast notification)
        console.log(`✅ Exported ${filteredTeachers.length} professors to ${filename}`);
      }
    } catch (error) {
      console.error('❌ Export failed:', error);
      // You can add a toast notification here for user feedback
    }
  };

  // Fetch detailed teacher information including Google Scholar data
  const fetchTeacherDetails = async (teacherId) => {
    try {
      setLoadingDetails(true);
      const response = await fetch(`http://localhost:5000/api/professors/${teacherId}?include_citations=true`);
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
    setAiServerResults(null);
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
                        )) || details.domain_expertise?.split(' | ').map((domain, index) => (
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
                          {details.domain_expertise.split(' | ').map((area, index) => (
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
          <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-cyan-500 font-sans tracking-tight mb-4 leading-[1.34]">
            AI-Powered Faculty Research Directory
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
              <input
                type="text"
                placeholder="Search by name, skill, or domain (AI-backed)"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full p-4 pl-12 pr-16 text-lg border border-gray-300 dark:border-gray-600 rounded-full 
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                           focus:ring-2 focus:ring-blue-500 focus:border-transparent 
                           transition duration-300 shadow-lg"
              />
              <div className="absolute right-4 top-1/2 transform -translate-y-1/2 flex items-center gap-2">
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
                      onClick={() => setSearchTerm(suggestion)}
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
              {/* College Filter Dropdown */}
              <div className="relative w-full sm:w-auto">
                <select
                  value={filterBy}
                  onChange={(e) => setFilterBy(e.target.value)}
                  className="w-full sm:w-auto appearance-none bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 pr-8 text-sm font-medium text-gray-700 dark:text-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-sm"
                >
                  <option value="all">All Colleges ({teachers.length} professors)</option>
                  {availableColleges.length > 0 && (
                    <>
                      {availableColleges.map((college, index) => {
                        // Count teachers for this normalized college name
                        const teacherCount = teachers.filter(teacher => {
                          if (!teacher.college) return false;
                          const normalizedTeacherCollege = teacher.college.trim()
                            .toLowerCase()
                            .split(' ')
                            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                            .join(' ');
                          return normalizedTeacherCollege === college;
                        }).length;
                        
                        return (
                          <option key={index} value={college}>
                            {college} ({teacherCount} professors)
                          </option>
                        );
                      })}
                    </>
                  )}
                </select>
                <Filter className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>

              {/* Sort Options */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 w-full sm:w-auto">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">Sort by:</span>
                <div className="flex flex-wrap gap-2 w-full sm:w-auto">
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
                  <button
                    onClick={() => handleSort('citations')}
                    title={`Sort by citations (${sortOrder === 'asc' ? 'highest first' : 'lowest first'})`}
                    className={`flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm flex-1 sm:flex-none justify-center ${
                      sortBy === 'citations' 
                        ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300' 
                        : 'bg-white text-gray-600 hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700'
                    }`}
                  >
                    <Award className="w-3 h-3 mr-1" />
                    Citations
                    {sortBy === 'citations' && (sortOrder === 'asc' ? <SortDesc className="w-4 h-4" /> : <SortAsc className="w-4 h-4" />)}
                  </button>
                  
                  {/* Export Button */}
                  <button
                    onClick={handleExport}
                    className="flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm flex-1 sm:flex-none justify-center bg-green-50 text-green-700 hover:bg-green-100 dark:bg-green-900/20 dark:text-green-300 dark:hover:bg-green-900/40 border border-green-200 dark:border-green-800"
                    title="Export filtered results to CSV"
                  >
                    <Download className="w-4 h-4" />
                    Export
                  </button>
                </div>
              </div>
            </div>

            {/* Right side - View Mode and Results Count */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between sm:justify-end gap-4 w-full lg:w-auto order-1 lg:order-2">
              {/* Results Count */}
              <span className="text-sm text-gray-600 dark:text-gray-400 font-medium order-2 sm:order-1 whitespace-nowrap">
                {loading ? 'Loading...' : (
                  `${filteredTeachers.length} results${filterBy && filterBy !== 'all' ? ` from ${filterBy}` : ''}${searchTerm ? '' : (filterBy && filterBy !== 'all') ? '' : ' '}`
                )}
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
                <div className="w-full max-w-none mx-auto grid gap-6 grid-cols-3">
                  {filteredTeachers.length > 0 ? (
                    filteredTeachers.map(teacher => (
                      <div key={teacher.id} className="group relative bg-white rounded-3xl shadow-lg hover:shadow-2xl transform hover:-translate-y-2 transition-all duration-500 border border-gray-100 overflow-hidden dark:bg-gray-800 dark:border-gray-700 h-[540px] flex flex-col">
                        {/* Card Header with Gradient Background */}
                        <div className="relative p-4 md:p-6 pb-4 bg-gradient-to-br from-indigo-50 via-blue-50 to-cyan-50 dark:from-gray-700 dark:via-gray-800 dark:to-gray-900 flex-shrink-0">
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
                              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1 line-clamp-2 group-hover:text-blue-600 transition-colors duration-300">
                                {teacher.name}
                              </h3>
                              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
                                <MapPin className="w-4 h-4 flex-shrink-0" />
                                <span className="line-clamp-2">{teacher.college}</span>
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
                        <div className="p-6 pt-4 flex-grow flex flex-col overflow-hidden">
                          {/* Scrollable Content Area */}
                          <div className="flex-grow overflow-y-auto pr-1 card-content-scrollable">
                          {/* Citation Metrics */}
                          {(teacher.citations_count > 0 || teacher.h_index > 0 || teacher.i10_index > 0) && (
                            <div className="mb-4 flex-shrink-0">
                              <div className="flex items-center gap-2 mb-2">
                                <Award className="w-4 h-4 text-yellow-500" />
                                <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Academic Impact</span>
                              </div>
                              <div className="grid grid-cols-3 gap-2">
                                {teacher.citations_count > 0 && (
                                  <div className={`p-2 ${
                                    teacher.citations_count > 1000 
                                      ? 'bg-gradient-to-br from-blue-100 to-blue-200 dark:from-blue-900/40 dark:to-blue-800/40' 
                                      : 'bg-blue-50 dark:bg-blue-900/20'
                                  } rounded-lg text-center relative`}>
                                    {teacher.citations_count > 1000 && (
                                      <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full flex items-center justify-center">
                                        <div className="text-xs text-yellow-800">★</div>
                                      </div>
                                    )}
                                    <div className="text-blue-700 dark:text-blue-300 font-bold">{teacher.citations_count}</div>
                                    <div className="text-xs text-blue-600 dark:text-blue-400">Citations</div>
                                  </div>
                                )}
                                {teacher.h_index > 0 && (
                                  <div className={`p-2 ${
                                    teacher.h_index > 20 
                                      ? 'bg-gradient-to-br from-green-100 to-green-200 dark:from-green-900/40 dark:to-green-800/40' 
                                      : 'bg-green-50 dark:bg-green-900/20'
                                  } rounded-lg text-center relative`}>
                                    {teacher.h_index > 20 && (
                                      <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full flex items-center justify-center">
                                        <div className="text-xs text-yellow-800">★</div>
                                      </div>
                                    )}
                                    <div className="text-green-700 dark:text-green-300 font-bold">{teacher.h_index}</div>
                                    <div className="text-xs text-green-600 dark:text-green-400">h-index</div>
                                  </div>
                                )}
                                {teacher.i10_index > 0 && (
                                  <div className={`p-2 ${
                                    teacher.i10_index > 20 
                                      ? 'bg-gradient-to-br from-purple-100 to-purple-200 dark:from-purple-900/40 dark:to-purple-800/40' 
                                      : 'bg-purple-50 dark:bg-purple-900/20'
                                  } rounded-lg text-center relative`}>
                                    {teacher.i10_index > 20 && (
                                      <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full flex items-center justify-center">
                                        <div className="text-xs text-yellow-800">★</div>
                                      </div>
                                    )}
                                    <div className="text-purple-700 dark:text-purple-300 font-bold">{teacher.i10_index}</div>
                                    <div className="text-xs text-purple-600 dark:text-purple-400">i10-index</div>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}

                          {/* Research Areas */}
                          <div className="mb-4 flex-shrink-0">
                            <div className="flex items-center gap-2 mb-2">
                              <Briefcase className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Research Areas</span>
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {teacher.domain_expertise?.split(' | ').slice(0, 3).map((domain, index) => (
                                <span 
                                  key={index} 
                                  className="px-3 py-1.5 bg-gradient-to-r from-blue-500 to-cyan-500 text-white text-xs font-medium rounded-full shadow-sm hover:shadow-md transition-shadow duration-300"
                                >
                                  {domain.trim()}
                                </span>
                              ))}
                              {teacher.domain_expertise?.split(' | ').length > 3 && (
                                <span className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs font-medium rounded-full border border-gray-200 dark:border-gray-600">
                                  +{teacher.domain_expertise.split(' | ').length - 3} more
                                </span>
                              )}
                            </div>
                          </div>                          {/* Academic Profiles Links */}
                          <div className="mb-4">
                            <div className="flex items-center gap-2 mb-2">
                              <Award className="w-4 h-4 text-yellow-500" />
                              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Academic Profiles</span>
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
                              {!teacher.google_scholar_url && !teacher.semantic_scholar_url && !teacher.profile_link && (
                                <span className="px-2 py-1 bg-gray-50 border border-gray-200 text-gray-500 text-xs rounded-lg">
                                  No profiles available
                                </span>
                              )}
                            </div>
                          </div>

                          </div> {/* End of scrollable content area */}

                          {/* Action Button - Fixed at the bottom */}
                          <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700 flex-shrink-0">
                            <button
                              onClick={() => handleTeacherClick(teacher)}
                              className="w-full py-3 px-4 text-white font-semibold rounded-2xl shadow-lg bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 hover:from-blue-700 hover:via-purple-700 hover:to-indigo-700 transform hover:scale-105 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 flex items-center justify-center gap-3 group-hover:shadow-xl text-sm"
                            >
                              <Eye className="w-4 h-4 transform group-hover:scale-110 transition-transform duration-300" />
                              <span>View Full Profile</span>
                              <ExternalLink className="w-4 h-4 opacity-70" />
                            </button>
                          </div>
                        </div>

                        {/* Hover Effect Overlay */}
                        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 to-purple-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none rounded-3xl"></div>
                      </div>
                    ))
                  ) : (
                    <div className="col-span-full text-center py-12">
                      <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                        No professors found
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400 mb-4">
                        {searchTerm ? `No professors found matching "${searchTerm}". Try a different search term.` : 'No professors match the selected filters.'}
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
                                  {teacher.domain_expertise?.split(' | ').slice(0, 4).map((domain, index) => (
                                    <span 
                                      key={index} 
                                      className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-full"
                                    >
                                      {domain.trim()}
                                    </span>
                                  ))}
                                  {teacher.domain_expertise?.split(' | ').length > 4 && (
                                    <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded-full">
                                      +{teacher.domain_expertise.split(' | ').length - 4} more
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

                                {/* Citation Metrics */}
                                {(teacher.citations_count > 0 || teacher.h_index > 0 || teacher.i10_index > 0) && (
                                  <div className="flex items-center gap-3 mb-3">
                                    <div className="flex items-center gap-2">
                                      <Award className="w-4 h-4 text-yellow-500" />
                                      <span className="text-xs font-medium text-gray-600 dark:text-gray-400">Impact:</span>
                                    </div>
                                    <div className="flex gap-2">
                                      {teacher.citations_count > 0 && (
                                        <span className="px-2 py-1 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300 text-xs rounded flex items-center gap-1">
                                          <span className="font-bold">{teacher.citations_count}</span> Citations
                                        </span>
                                      )}
                                      {teacher.h_index > 0 && (
                                        <span className="px-2 py-1 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-300 text-xs rounded flex items-center gap-1">
                                          h-index: <span className="font-bold">{teacher.h_index}</span>
                                        </span>
                                      )}
                                      {teacher.i10_index > 0 && (
                                        <span className="px-2 py-1 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 text-purple-700 dark:text-purple-300 text-xs rounded flex items-center gap-1">
                                          i10-index: <span className="font-bold">{teacher.i10_index}</span>
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                )}

                                {/* Academic Links */}
                                <div className="flex items-center gap-3">
                                  <div className="flex items-center gap-2">
                                    <GraduationCap className="w-4 h-4 text-blue-500" />
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
                                        No profiles available
                                      </span>
                                    )}
                                  </div>
                                </div>
                              </div>

                              {/* Status Indicators & Actions */}
                              <div className="flex-shrink-0 flex items-center gap-3">
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
                            Search our comprehensive database of professors to discover their research profiles, PhD thesis topics, academic affiliations, and publication data.
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
                            No professors found
                          </h3>
                          <p className="text-gray-600 dark:text-gray-400 mb-4">
                            {searchTerm ? `No professors found matching "${searchTerm}". Try a different search term.` : 'No professors match the selected filters.'}
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