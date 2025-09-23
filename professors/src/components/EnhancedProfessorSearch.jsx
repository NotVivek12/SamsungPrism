import React, { useState, useEffect } from 'react';
import { Search, Users, GraduationCap, Mail, ArrowLeft } from 'lucide-react';

const SimpleProfessorSearch = ({ onProfessorSelect = null }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [professors, setProfessors] = useState([]);
  const [filteredProfessors, setFilteredProfessors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProfessor, setSelectedProfessor] = useState(null);

  // Sample data fallback
  const sampleProfessors = [
    {
      id: 1,
      name: "Dr. Sarah Johnson",
      institute: "MIT",
      domain: "Artificial Intelligence",
      email: "sarah.johnson@mit.edu",
      citations: 1250,
      hIndex: 24,
      totalPublications: 45,
      researchInterests: ["Machine Learning", "Neural Networks", "Computer Vision"],
      bio: "Dr. Johnson is a leading researcher in artificial intelligence with over 15 years of experience.",
      education: "PhD in Computer Science, Stanford University",
      experience: "Professor at MIT since 2015, previously at Google Research",
      projects: ["Autonomous Driving AI", "Medical Image Analysis", "Natural Language Processing"],
      researchPapers: ["Deep Learning for Medical Diagnosis", "Neural Network Optimization", "Computer Vision in Robotics"]
    },
    {
      id: 2,
      name: "Prof. Michael Chen",
      institute: "Stanford University", 
      domain: "Machine Learning",
      email: "m.chen@stanford.edu",
      citations: 890,
      hIndex: 19,
      totalPublications: 32,
      researchInterests: ["Deep Learning", "Reinforcement Learning", "Data Science"],
      bio: "Professor Chen specializes in machine learning applications in healthcare and finance.",
      education: "PhD in Statistics, UC Berkeley",
      experience: "Associate Professor at Stanford, former Data Scientist at Facebook",
      projects: ["Healthcare Analytics", "Financial Prediction Models", "Automated Trading Systems"],
      researchPapers: ["Reinforcement Learning in Finance", "Healthcare Data Mining", "Deep Learning Applications"]
    },
    {
      id: 3,
      name: "Dr. Emily Rodriguez",
      institute: "Carnegie Mellon University",
      domain: "Computer Vision",
      email: "e.rodriguez@cmu.edu", 
      citations: 670,
      hIndex: 16,
      totalPublications: 28,
      researchInterests: ["Image Processing", "Pattern Recognition", "Augmented Reality"],
      bio: "Dr. Rodriguez is an expert in computer vision with focus on real-world applications.",
      education: "PhD in Electrical Engineering, Caltech",
      experience: "Assistant Professor at CMU, former researcher at Microsoft Research",
      projects: ["Augmented Reality Systems", "Medical Image Processing", "Autonomous Vehicle Vision"],
      researchPapers: ["Advanced Image Recognition", "AR in Education", "Vision-Based Navigation"]
    }
  ];

  // Load professors data
  useEffect(() => {
    const loadProfessors = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Try to fetch from API first
        try {
          const response = await fetch('http://localhost:5000/api/professors');
          if (response.ok) {
            const data = await response.json();
            if (data && data.length > 0) {
              setProfessors(data);
              setFilteredProfessors(data);
              return;
            }
          }
        } catch (apiError) {
          console.log('API not available, using sample data');
        }
        
        // Fallback to sample data
        setProfessors(sampleProfessors);
        setFilteredProfessors(sampleProfessors);
        
      } catch (err) {
        setError('Failed to load professors data');
        setProfessors(sampleProfessors);
        setFilteredProfessors(sampleProfessors);
      } finally {
        setLoading(false);
      }
    };

    loadProfessors();
  }, []);

  // Filter professors based on search criteria
  useEffect(() => {
    let filtered = professors;

    // Simple text search
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(professor => 
        professor.name?.toLowerCase().includes(term) ||
        professor.domain?.toLowerCase().includes(term) ||
        professor.institute?.toLowerCase().includes(term) ||
        professor.email?.toLowerCase().includes(term)
      );
    }

    setFilteredProfessors(filtered);
  }, [searchTerm, professors]);

  // Clear search
  const clearSearch = () => {
    setSearchTerm('');
  };

  // Handle professor selection
  const handleProfessorClick = (professor) => {
    if (onProfessorSelect) {
      onProfessorSelect(professor);
    } else {
      setSelectedProfessor(professor);
    }
  };

  // Profile Page Component
  const ProfilePage = ({ professor, onBack }) => {
    if (!professor) return null;

    return (
      <div className="p-6 bg-white rounded-2xl shadow-xl dark:bg-slate-800">
        <button
          onClick={onBack}
          className="flex items-center text-blue-600 hover:underline mb-6 font-semibold dark:text-blue-400"
        >
          <ArrowLeft className="w-5 h-5 mr-2" /> Back to Search
        </button>

        <div className="flex flex-col items-center mb-6">
          <img
            src={`https://placehold.co/150x150/e5e7eb/6b7280?text=${professor.name ? professor.name.split(' ').map(n => n[0]).join('') : '??'}`}
            alt={professor.name || 'Professor'}
            className="rounded-full shadow-lg mb-4"
          />
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-cyan-500">{professor.name || 'Unknown Professor'}</h1>
          <p className="text-xl text-gray-600 dark:text-slate-400">{professor.domain || 'Domain not specified'} at {professor.institute || 'Institution not specified'}</p>
          <p className="text-sm text-gray-500 dark:text-slate-500 mt-1">Email: {professor.email || 'Not available'}</p>
          
          {/* Citation metrics */}
          {(professor.citations > 0 || professor.hIndex > 0) && (
            <div className="flex gap-4 mt-3 text-sm text-gray-600 dark:text-slate-400">
              {professor.citations > 0 && <span>Citations: {professor.citations}</span>}
              {professor.hIndex > 0 && <span>H-Index: {professor.hIndex}</span>}
              {professor.totalPublications > 0 && <span>Publications: {professor.totalPublications}</span>}
            </div>
          )}
        </div>

        <div className="space-y-6">
          {professor.bio && (
            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2 dark:text-white">Biography</h2>
              <p className="text-gray-700 dark:text-slate-300">{professor.bio}</p>
            </div>
          )}
          
          {professor.education && (
            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2 dark:text-white">Education</h2>
              <p className="text-gray-700 dark:text-slate-300">{professor.education}</p>
            </div>
          )}
          
          {professor.experience && (
            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2 dark:text-white">Experience</h2>
              <p className="text-gray-700 dark:text-slate-300">{professor.experience}</p>
            </div>
          )}
          
          {professor.projects && professor.projects.length > 0 && (
            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2 dark:text-white">Key Projects</h2>
              <ul className="list-disc list-inside text-gray-700 dark:text-slate-300">
                {professor.projects.map((project, index) => (
                  <li key={index}>{project}</li>
                ))}
              </ul>
            </div>
          )}
          
          {professor.researchPapers && professor.researchPapers.length > 0 && (
            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2 dark:text-white">Research Papers</h2>
              <ul className="list-disc list-inside text-gray-700 dark:text-slate-300">
                {professor.researchPapers.map((paper, index) => (
                  <li key={index}>{paper}</li>
                ))}
              </ul>
            </div>
          )}
          
          {professor.researchInterests && professor.researchInterests.length > 0 && (
            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2 dark:text-white">Research Interests</h2>
              <div className="flex flex-wrap gap-2">
                {professor.researchInterests.map((interest, index) => (
                  <span 
                    key={index}
                    className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm dark:bg-blue-900 dark:text-blue-200"
                  >
                    {interest}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  // Show profile page if professor is selected
  if (selectedProfessor) {
    return <ProfilePage professor={selectedProfessor} onBack={() => setSelectedProfessor(null)} />;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-cyan-500 font-sans tracking-tight mb-4">
            Search for Professors
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            Find experts by their domain of expertise.
          </p>
        </div>

        {/* Simple Search Bar */}
        <div className="w-full max-w-2xl mx-auto mb-8">
          <div className="relative">
            <input
              type="text"
              placeholder="Describe your Project (e.g., 'Artificial Intelligence')"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full p-4 pl-12 pr-4 text-lg border border-gray-300 rounded-full shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-300 dark:bg-slate-700 dark:text-white dark:border-slate-600"
            />
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-6 h-6" />
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="w-full max-w-4xl mx-auto text-center py-10">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-lg text-gray-600">Loading professors data...</p>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="w-full max-w-4xl mx-auto text-center py-10">
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              <strong className="font-bold">Error: </strong>
              <span className="block sm:inline">{error}</span>
            </div>
            <p className="text-gray-600">
              Unable to load professors data. Please make sure the backend server is running on localhost:5000.
            </p>
          </div>
        )}

        {/* Professor Results - Simple Card Layout */}
        {!loading && !error && (
          <div className="w-full max-w-4xl mx-auto grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filteredProfessors.length > 0 ? (
              filteredProfessors.map(professor => (
                <div key={professor.id} className="bg-white p-6 rounded-2xl shadow-xl hover:shadow-2xl transform hover:scale-105 transition duration-300 border border-gray-200 flex flex-col items-start dark:bg-slate-800 dark:border-slate-700">
                  <h3 className="text-xl font-semibold text-gray-800 dark:text-white">{professor.name || 'Unknown Professor'}</h3>
                  <p className="text-gray-600 mt-2 text-sm font-medium dark:text-slate-400">Domain: {professor.domain || 'Not specified'}</p>
                  <p className="text-gray-600 text-sm font-medium dark:text-slate-400">Institute: {professor.institute || 'Not specified'}</p>
                  {professor.citations > 0 && (
                    <p className="text-gray-500 text-xs mt-1">Citations: {professor.citations}</p>
                  )}
                  <button
                    onClick={() => handleProfessorClick(professor)}
                    className="mt-4 px-6 py-2 text-white font-semibold rounded-full shadow-lg bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 transition duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    View Profile
                  </button>
                </div>
              ))
            ) : (
              <div className="col-span-full text-center py-10">
                {searchTerm ? (
                  <div>
                    <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                      No professors found
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                      No professors found matching "{searchTerm}". Try a different search term.
                    </p>
                    <button
                      onClick={clearSearch}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
                    >
                      Clear Search
                    </button>
                  </div>
                ) : professors.length === 0 ? (
                  <div className="text-center">
                    <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-lg text-gray-500 mb-4">No professors data available.</p>
                    <p className="text-sm text-gray-400">
                      Upload an Excel file with professor data using the /extract endpoint to populate the database.
                    </p>
                  </div>
                ) : (
                  <div>
                    <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-lg text-gray-500">No professors found for that domain. Try a different search term.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SimpleProfessorSearch;