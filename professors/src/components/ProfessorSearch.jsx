import React, { useState, useEffect } from 'react';
import { Search, Users, GraduationCap, Globe, Mail, ExternalLink, Filter, X } from 'lucide-react';

const ProfessorSearch = () => {
  const [professors, setProfessors] = useState([]);
  const [filteredProfessors, setFilteredProfessors] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  // API base URL
  const API_BASE_URL = 'http://localhost:5000/api';

  // Load professors from our teacher database
  useEffect(() => {
    loadProfessors();
  }, []);

  // Filter professors based on search term and domain
  useEffect(() => {
    filterProfessors();
  }, [searchTerm, selectedDomain, professors]);

  const loadProfessors = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Try to load from API first, fall back to local data
      const response = await fetch(`${API_BASE_URL}/professors`);
      if (response.ok) {
        const data = await response.json();
        setProfessors(data);
      } else {
        // Load sample data if API is not available
        loadSampleData();
      }
    } catch (err) {
      console.warn('API not available, loading sample data:', err);
      loadSampleData();
    } finally {
      setLoading(false);
    }
  };

  const loadSampleData = () => {
    // Sample professor data based on the extracted teachers
    const sampleProfessors = [
      {
        id: 1,
        name: 'Dr. Jayakumar Sadhasivam',
        domain: 'Network and Cyber Security, AI, Web3.0',
        institute: 'Vellore Institute of Technology, Vellore',
        email: 'jayakumars@vit.ac.in',
        researchInterests: ['AI', 'Cybersecurity', 'Web3.0'],
        citations: 1250,
        hIndex: 25,
        totalPublications: 45
      },
      {
        id: 2,
        name: 'Ramesh Ashok Tabib',
        domain: 'Visual Intelligence, GenAI, Computer Vision',
        institute: 'KLE Technological University',
        email: 'ramesh_t@kletech.ac.in',
        researchInterests: ['Computer Vision', 'GenAI', 'Visual Intelligence'],
        citations: 890,
        hIndex: 22,
        totalPublications: 38
      },
      {
        id: 3,
        name: 'Dr. Sowmya BJ',
        domain: 'Artificial Intelligence, Machine learning, Quantum Computing, Security',
        institute: 'Ramaiah Institute of Technology',
        email: 'sowmyabj@msrit.edu',
        researchInterests: ['AI', 'Machine Learning', 'Quantum Computing'],
        citations: 756,
        hIndex: 19,
        totalPublications: 32
      },
      {
        id: 4,
        name: 'Dr.K.Panimozhi',
        domain: 'IoT, AI, ML, Big data',
        institute: 'B.M.S College Of Engineering',
        email: 'panimozhi.cse@bmsce.ac.in',
        researchInterests: ['IoT', 'AI', 'Machine Learning', 'Big Data'],
        citations: 634,
        hIndex: 18,
        totalPublications: 29
      },
      {
        id: 5,
        name: 'Rajeswari Sridhar',
        domain: 'NLP, Machine learning, Deep learning, Reinforcement learning, Cloud',
        institute: 'National Institute of Technology Tiruchirappalli',
        email: 'rajeswaris@nitt.edu',
        researchInterests: ['NLP', 'Machine Learning', 'Deep Learning'],
        citations: 523,
        hIndex: 16,
        totalPublications: 27
      }
    ];
    setProfessors(sampleProfessors);
  };

  const filterProfessors = () => {
    let filtered = professors;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(prof =>
        prof.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        prof.domain.toLowerCase().includes(searchTerm.toLowerCase()) ||
        prof.institute.toLowerCase().includes(searchTerm.toLowerCase()) ||
        prof.researchInterests?.some(interest => 
          interest.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Filter by domain
    if (selectedDomain) {
      filtered = filtered.filter(prof =>
        prof.domain.toLowerCase().includes(selectedDomain.toLowerCase()) ||
        prof.researchInterests?.some(interest => 
          interest.toLowerCase().includes(selectedDomain.toLowerCase())
        )
      );
    }

    setFilteredProfessors(filtered);
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedDomain('');
    setShowFilters(false);
  };

  const getUniqueDomains = () => {
    const domains = new Set();
    professors.forEach(prof => {
      if (prof.researchInterests) {
        prof.researchInterests.forEach(interest => domains.add(interest));
      }
    });
    return Array.from(domains).sort();
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Professor Search
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Find professors and researchers by expertise, domain, or institution
          </p>
        </div>

        {/* Search and Filter Controls */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search Input */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by name, domain, or institution..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg 
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                         focus:ring-2 focus:ring-blue-500 focus:border-transparent
                         placeholder-gray-500 dark:placeholder-gray-400"
              />
            </div>

            {/* Filter Toggle */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 
                       transition-colors duration-200 flex items-center gap-2"
            >
              <Filter className="w-5 h-5" />
              Filters
            </button>

            {/* Clear Filters */}
            {(searchTerm || selectedDomain) && (
              <button
                onClick={clearFilters}
                className="px-4 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 
                         transition-colors duration-200 flex items-center gap-2"
              >
                <X className="w-5 h-5" />
                Clear
              </button>
            )}
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Research Domain
                  </label>
                  <select
                    value={selectedDomain}
                    onChange={(e) => setSelectedDomain(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                             bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                             focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">All Domains</option>
                    {getUniqueDomains().map(domain => (
                      <option key={domain} value={domain}>{domain}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Results Count */}
        <div className="mb-4">
          <p className="text-gray-600 dark:text-gray-400">
            {loading ? 'Loading...' : `Found ${filteredProfessors.length} professor${filteredProfessors.length !== 1 ? 's' : ''}`}
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {/* Professor Results Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProfessors.map(professor => (
            <div key={professor.id} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
              <div className="p-6">
                {/* Professor Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                      {professor.name}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1">
                      <GraduationCap className="w-4 h-4" />
                      {professor.institute}
                    </p>
                  </div>
                </div>

                {/* Domain Expertise */}
                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Domain Expertise:
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {professor.domain}
                  </p>
                </div>

                {/* Research Interests Tags */}
                {professor.researchInterests && (
                  <div className="mb-4">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Research Interests:
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {professor.researchInterests.slice(0, 3).map((interest, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 
                                   text-xs rounded-full"
                        >
                          {interest}
                        </span>
                      ))}
                      {professor.researchInterests.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 
                                       text-xs rounded-full">
                          +{professor.researchInterests.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Stats */}
                {professor.citations && (
                  <div className="mb-4 grid grid-cols-3 gap-2 text-center">
                    <div className="bg-gray-50 dark:bg-gray-700 rounded p-2">
                      <p className="text-xs text-gray-500 dark:text-gray-400">Citations</p>
                      <p className="font-semibold text-gray-900 dark:text-white">{professor.citations}</p>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700 rounded p-2">
                      <p className="text-xs text-gray-500 dark:text-gray-400">h-index</p>
                      <p className="font-semibold text-gray-900 dark:text-white">{professor.hIndex}</p>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700 rounded p-2">
                      <p className="text-xs text-gray-500 dark:text-gray-400">Publications</p>
                      <p className="font-semibold text-gray-900 dark:text-white">{professor.totalPublications}</p>
                    </div>
                  </div>
                )}

                {/* Contact */}
                <div className="pt-4 border-t border-gray-200 dark:border-gray-600">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <Mail className="w-4 h-4" />
                      <span className="truncate">{professor.email}</span>
                    </div>
                    <button className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300">
                      <ExternalLink className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {!loading && filteredProfessors.length === 0 && (
          <div className="text-center py-12">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No professors found
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Try adjusting your search criteria or clearing filters
            </p>
            <button
              onClick={clearFilters}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
            >
              Clear Filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfessorSearch;