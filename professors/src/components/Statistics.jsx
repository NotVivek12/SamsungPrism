jjkhhlkimport React, { useState, useEffect, useRef, useCallback } from 'react';
import { ArrowLeft, BarChart3, Users, Award, TrendingUp, Building, BookOpen, Network, X, Mail, ExternalLink, Maximize2, Minimize2, ZoomIn, ZoomOut, RotateCcw, ChevronRight, Search } from 'lucide-react';

// Color palette for expertise domains
const domainColors = {
  'Machine Learning': '#3B82F6',
  'Artificial Intelligence': '#8B5CF6',
  'Data Science': '#10B981',
  'Computer Vision': '#F59E0B',
  'Natural Language Processing': '#EF4444',
  'Deep Learning': '#EC4899',
  'Cybersecurity': '#6366F1',
  'Software Engineering': '#14B8A6',
  'Database Systems': '#F97316',
  'Networks': '#84CC16',
  'Robotics': '#06B6D4',
  'Cloud Computing': '#A855F7',
  'IoT': '#22C55E',
  'Blockchain': '#EAB308',
  'default': '#6B7280'
};

// Get color for a domain
const getDomainColor = (domain) => {
  if (!domain) return domainColors.default;
  const normalizedDomain = domain.toLowerCase();
  for (const [key, color] of Object.entries(domainColors)) {
    if (normalizedDomain.includes(key.toLowerCase()) || key.toLowerCase().includes(normalizedDomain)) {
      return color;
    }
  }
  // Generate a consistent color based on domain name hash
  let hash = 0;
  for (let i = 0; i < domain.length; i++) {
    hash = domain.charCodeAt(i) + ((hash << 5) - hash);
  }
  const colors = Object.values(domainColors).filter(c => c !== domainColors.default);
  return colors[Math.abs(hash) % colors.length];
};

// Professor Profile Modal
const ProfileModal = ({ professor, onClose }) => {
  if (!professor) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white dark:bg-gray-800 p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Professor Profile</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
        </div>
        
        <div className="p-6">
          {/* Header with photo */}
          <div className="flex items-start gap-4 mb-6">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold flex-shrink-0 overflow-hidden">
              {professor.profile_picture_url || professor.scholar_profile_picture ? (
                <img 
                  src={professor.profile_picture_url || professor.scholar_profile_picture} 
                  alt={professor.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                professor.name?.charAt(0) || 'P'
              )}
            </div>
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{professor.name}</h3>
              {professor.college && (
                <p className="text-gray-600 dark:text-gray-400 flex items-center gap-2 mt-1">
                  <Building className="w-4 h-4" />
                  {professor.college}
                </p>
              )}
              {professor.email && (
                <a 
                  href={`mailto:${professor.email}`}
                  className="text-blue-600 dark:text-blue-400 flex items-center gap-2 mt-1 hover:underline"
                >
                  <Mail className="w-4 h-4" />
                  {professor.email}
                </a>
              )}
            </div>
          </div>

          {/* Domain Expertise */}
          {professor.domain_expertise && (
            <div className="mb-6">
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Domain Expertise</h4>
              <div className="flex flex-wrap gap-2">
                {professor.domain_expertise.split(',').map((domain, i) => (
                  <span 
                    key={i}
                    className="px-3 py-1 rounded-full text-sm font-medium text-white"
                    style={{ backgroundColor: getDomainColor(domain.trim()) }}
                  >
                    {domain.trim()}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Research Interests */}
          {professor.research_interests && (
            <div className="mb-6">
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Research Interests</h4>
              <p className="text-gray-700 dark:text-gray-300">{professor.research_interests}</p>
            </div>
          )}

          {/* PhD Thesis */}
          {professor.phd_thesis && (
            <div className="mb-6">
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">PhD Thesis</h4>
              <p className="text-gray-700 dark:text-gray-300">{professor.phd_thesis}</p>
            </div>
          )}

          {/* Citation Metrics */}
          {(professor.citations_count || professor.h_index || professor.i10_index) && (
            <div className="mb-6">
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Citation Metrics</h4>
              <div className="grid grid-cols-3 gap-4">
                {professor.citations_count > 0 && (
                  <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-xl text-center">
                    <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{professor.citations_count}</p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">Citations</p>
                  </div>
                )}
                {professor.h_index > 0 && (
                  <div className="bg-purple-50 dark:bg-purple-900/20 p-3 rounded-xl text-center">
                    <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">{professor.h_index}</p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">h-index</p>
                  </div>
                )}
                {professor.i10_index > 0 && (
                  <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-xl text-center">
                    <p className="text-2xl font-bold text-green-600 dark:text-green-400">{professor.i10_index}</p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">i10-index</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* External Links */}
          <div className="flex flex-wrap gap-3">
            {professor.google_scholar_url && (
              <a
                href={professor.google_scholar_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
              >
                <ExternalLink className="w-4 h-4" />
                Google Scholar
              </a>
            )}
            {professor.profile_link && (
              <a
                href={professor.profile_link}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-lg hover:bg-purple-200 dark:hover:bg-purple-900/50 transition-colors"
              >
                <ExternalLink className="w-4 h-4" />
                University Profile
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Expertise Professors List Modal - Shows all professors in a domain
const ExpertiseListModal = ({ expertise, professors, onClose, onSelectProfessor }) => {
  const [searchTerm, setSearchTerm] = useState('');
  
  if (!expertise) return null;
  
  // Filter professors by expertise and search term
  const filteredProfessors = professors
    .filter(p => p.domain_expertise?.toLowerCase().includes(expertise.toLowerCase()))
    .filter(p => 
      !searchTerm || 
      p.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.college?.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => (b.citations_count || 0) - (a.citations_count || 0));

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-3xl w-full max-h-[85vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-800 p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex justify-between items-center mb-3">
            <div className="flex items-center gap-3">
              <div 
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: getDomainColor(expertise) }}
              ></div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">{expertise}</h2>
              <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-full text-sm text-gray-600 dark:text-gray-400">
                {filteredProfessors.length} professors
              </span>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
            >
              <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>
          </div>
          
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search professors by name or college..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-100 dark:bg-gray-700 border-none rounded-lg text-gray-900 dark:text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>
        </div>
        
        {/* Professor List */}
        <div className="flex-1 overflow-y-auto p-4">
          {filteredProfessors.length > 0 ? (
            <div className="space-y-3">
              {filteredProfessors.map((professor, index) => (
                <div
                  key={professor.id || index}
                  onClick={() => {
                    onSelectProfessor(professor);
                    onClose();
                  }}
                  className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold flex-shrink-0 overflow-hidden">
                      {professor.profile_picture_url || professor.scholar_profile_picture ? (
                        <img 
                          src={professor.profile_picture_url || professor.scholar_profile_picture} 
                          alt={professor.name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        professor.name?.charAt(0) || 'P'
                      )}
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-white">{professor.name}</p>
                      {professor.college && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">{professor.college}</p>
                      )}
                      {professor.research_interests && (
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1 line-clamp-1">
                          {professor.research_interests}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    {professor.citations_count > 0 && (
                      <div className="text-right">
                        <p className="font-bold text-blue-600 dark:text-blue-400">{professor.citations_count}</p>
                        <p className="text-xs text-gray-500">citations</p>
                      </div>
                    )}
                    <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">No professors found matching your search.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Knowledge Graph Component - Expertise-focused with citation-based sizing
const KnowledgeGraph = ({ professors, onSelectProfessor, isFullscreen, onToggleFullscreen, availableExpertise = [] }) => {
  const svgRef = useRef(null);
  const containerRef = useRef(null);
  const [nodes, setNodes] = useState([]);
  const [links, setLinks] = useState([]);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [hoveredNode, setHoveredNode] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const [selectedExpertise, setSelectedExpertise] = useState(null);
  const [expertiseSearch, setExpertiseSearch] = useState('');
  const [showExpertiseDropdown, setShowExpertiseDropdown] = useState(false);

  // Get all unique expertise areas
  const allExpertiseAreas = React.useMemo(() => {
    const areas = new Set();
    professors.forEach(p => {
      if (p.domain_expertise) {
        p.domain_expertise.split(',').forEach(d => {
          const trimmed = d.trim();
          if (trimmed) areas.add(trimmed);
        });
      }
    });
    return Array.from(areas).sort();
  }, [professors]);

  // Filter expertise areas based on search
  const filteredExpertiseAreas = allExpertiseAreas.filter(area =>
    area.toLowerCase().includes(expertiseSearch.toLowerCase())
  );

  // Get max citations for scaling node sizes
  const maxCitations = React.useMemo(() => {
    return Math.max(...professors.map(p => p.citations_count || 0), 1);
  }, [professors]);

  // Calculate node size based on citations
  const getNodeSize = (citations) => {
    const minSize = 8;
    const maxSize = 30;
    const normalized = Math.sqrt((citations || 0) / maxCitations); // Square root for better distribution
    return minSize + normalized * (maxSize - minSize);
  };

  // Process professors data to create graph nodes and links
  useEffect(() => {
    if (!professors || professors.length === 0) return;

    const centerX = dimensions.width / 2;
    const centerY = dimensions.height / 2;

    // If an expertise is selected, show only that expertise and its professors
    if (selectedExpertise) {
      const matchingProfessors = professors.filter(p => 
        p.domain_expertise?.toLowerCase().includes(selectedExpertise.toLowerCase())
      );

      // Sort by citations for better visualization
      matchingProfessors.sort((a, b) => (b.citations_count || 0) - (a.citations_count || 0));

      // Create central expertise node
      const expertiseNode = {
        id: 'central-expertise',
        type: 'expertise',
        label: selectedExpertise,
        professors: matchingProfessors.map((_, i) => `prof-${i}`),
        x: centerX,
        y: centerY
      };

      // Create professor nodes arranged in a spiral based on citations
      const professorNodes = matchingProfessors.map((prof, index) => {
        const nodeSize = getNodeSize(prof.citations_count);
        // Spiral layout - higher cited professors closer to center
        const spiralFactor = 0.15;
        const baseAngle = index * 0.8; // Golden angle approximation for even distribution
        const radius = 80 + index * 25 * spiralFactor + nodeSize;
        const angle = baseAngle;
        
        return {
          id: `prof-${prof.id || index}`,
          type: 'professor',
          data: prof,
          label: prof.name || 'Unknown',
          citations: prof.citations_count || 0,
          nodeSize,
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle)
        };
      });

      // Create links from professors to central expertise
      const graphLinks = professorNodes.map(profNode => ({
        source: profNode.id,
        target: 'central-expertise',
        type: 'has_expertise'
      }));

      setNodes([expertiseNode, ...professorNodes]);
      setLinks(graphLinks);
    } else {
      // Default view: Show all expertise nodes with professors clustered around them
      const expertiseMap = new Map();
      const professorNodes = [];
      const graphLinks = [];

      // Create professor nodes and collect expertise
      professors.forEach((prof, index) => {
        const profNodeId = `prof-${prof.id || index}`;
        const nodeSize = getNodeSize(prof.citations_count);
        professorNodes.push({
          id: profNodeId,
          type: 'professor',
          data: prof,
          label: prof.name || 'Unknown',
          citations: prof.citations_count || 0,
          nodeSize,
          x: 0,
          y: 0
        });

        // Parse expertise domains
        if (prof.domain_expertise) {
          const domains = prof.domain_expertise.split(',').map(d => d.trim()).filter(d => d);
          domains.forEach(domain => {
            const normalizedDomain = domain.toLowerCase();
            if (!expertiseMap.has(normalizedDomain)) {
              expertiseMap.set(normalizedDomain, {
                id: `exp-${normalizedDomain.replace(/\s+/g, '-')}`,
                type: 'expertise',
                label: domain,
                professors: [],
                x: 0,
                y: 0
              });
            }
            expertiseMap.get(normalizedDomain).professors.push(profNodeId);
            graphLinks.push({
              source: profNodeId,
              target: `exp-${normalizedDomain.replace(/\s+/g, '-')}`,
              type: 'has_expertise'
            });
          });
        }
      });

      const expertiseNodes = Array.from(expertiseMap.values());
      
      // Position expertise nodes in a circle around the center
      const expertiseRadius = Math.min(dimensions.width, dimensions.height) * 0.35;
      expertiseNodes.forEach((node, i) => {
        const angle = (2 * Math.PI * i) / expertiseNodes.length;
        node.x = centerX + expertiseRadius * Math.cos(angle);
        node.y = centerY + expertiseRadius * Math.sin(angle);
      });

      // Position professor nodes near their primary expertise
      professorNodes.forEach((profNode, i) => {
        const prof = profNode.data;
        if (prof.domain_expertise) {
          const primaryDomain = prof.domain_expertise.split(',')[0].trim().toLowerCase();
          const expertiseNode = expertiseMap.get(primaryDomain);
          if (expertiseNode) {
            // Position professor near their expertise with offset based on citations
            const angle = Math.random() * 2 * Math.PI;
            const distance = 50 + Math.random() * 60 + (30 - profNode.nodeSize); // Higher cited closer
            profNode.x = expertiseNode.x + distance * Math.cos(angle);
            profNode.y = expertiseNode.y + distance * Math.sin(angle);
          } else {
            const angle = (2 * Math.PI * i) / professorNodes.length;
            const radius = expertiseRadius * 0.6 + Math.random() * 50;
            profNode.x = centerX + radius * Math.cos(angle);
            profNode.y = centerY + radius * Math.sin(angle);
          }
        } else {
          const angle = Math.random() * 2 * Math.PI;
          const radius = 100 + Math.random() * 150;
          profNode.x = centerX + radius * Math.cos(angle);
          profNode.y = centerY + radius * Math.sin(angle);
        }
      });

      setNodes([...professorNodes, ...expertiseNodes]);
      setLinks(graphLinks);
    }
  }, [professors, dimensions, selectedExpertise, maxCitations]);

  // Handle container resize
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setDimensions({ width: rect.width, height: rect.height });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, [isFullscreen]);

  // Pan handlers
  const handleMouseDown = useCallback((e) => {
    if (e.target === svgRef.current || e.target.tagName === 'svg') {
      setIsPanning(true);
      setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  }, [pan]);

  const handleMouseMove = useCallback((e) => {
    if (isPanning) {
      setPan({
        x: e.clientX - panStart.x,
        y: e.clientY - panStart.y
      });
    }
  }, [isPanning, panStart]);

  const handleMouseUp = useCallback(() => {
    setIsPanning(false);
  }, []);

  // Zoom handlers
  const handleZoomIn = () => setZoom(z => Math.min(z * 1.2, 3));
  const handleZoomOut = () => setZoom(z => Math.max(z / 1.2, 0.3));
  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setSelectedExpertise(null);
    setExpertiseSearch('');
  };

  // Handle expertise selection
  const handleSelectExpertise = (expertise) => {
    setSelectedExpertise(expertise);
    setExpertiseSearch(expertise);
    setShowExpertiseDropdown(false);
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  // Clear expertise filter
  const handleClearExpertise = () => {
    setSelectedExpertise(null);
    setExpertiseSearch('');
  };

  // Handle wheel zoom
  const handleWheel = useCallback((e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setZoom(z => Math.min(Math.max(z * delta, 0.3), 3));
  }, []);

  // Click handler for nodes
  const handleNodeClick = (node) => {
    if (node.type === 'professor') {
      onSelectProfessor(node.data);
    } else if (node.type === 'expertise') {
      // When clicking an expertise node, filter to show only that expertise
      if (node.id === 'central-expertise') {
        // If clicking the central node when already filtered, go back to all
        handleClearExpertise();
      } else {
        handleSelectExpertise(node.label);
      }
    }
  };

  // In filtered mode, all links are visible
  const visibleLinks = links;

  // In filtered mode, don't fade any professors
  const connectedProfessors = selectedExpertise
    ? new Set(nodes.filter(n => n.type === 'professor').map(n => n.id))
    : new Set();

  return (
    <div 
      ref={containerRef} 
      className={`relative bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-slate-800 rounded-2xl overflow-hidden ${isFullscreen ? 'fixed inset-0 z-40' : 'h-[500px]'}`}
    >
      {/* Expertise Search/Filter */}
      <div className="absolute top-4 left-4 z-20 w-72">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search or select expertise..."
            value={expertiseSearch}
            onChange={(e) => {
              setExpertiseSearch(e.target.value);
              setShowExpertiseDropdown(true);
            }}
            onFocus={() => setShowExpertiseDropdown(true)}
            className="w-full pl-10 pr-10 py-2.5 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl text-gray-900 dark:text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none shadow-lg text-sm"
          />
          {(selectedExpertise || expertiseSearch) && (
            <button
              onClick={handleClearExpertise}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-full"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>
          )}
        </div>
        
        {/* Expertise Dropdown */}
        {showExpertiseDropdown && filteredExpertiseAreas.length > 0 && !selectedExpertise && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl shadow-xl max-h-64 overflow-y-auto">
            {filteredExpertiseAreas.slice(0, 15).map((area, index) => {
              const count = professors.filter(p => 
                p.domain_expertise?.toLowerCase().includes(area.toLowerCase())
              ).length;
              return (
                <button
                  key={index}
                  onClick={() => handleSelectExpertise(area)}
                  className="w-full px-4 py-2.5 text-left hover:bg-gray-100 dark:hover:bg-gray-600 flex items-center justify-between gap-2 first:rounded-t-xl last:rounded-b-xl"
                >
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: getDomainColor(area) }}
                    ></div>
                    <span className="text-sm text-gray-900 dark:text-white">{area}</span>
                  </div>
                  <span className="text-xs text-gray-500 dark:text-gray-400">{count} professors</span>
                </button>
              );
            })}
          </div>
        )}

        {/* Selected expertise badge */}
        {selectedExpertise && (
          <div className="mt-2 flex items-center gap-2">
            <span 
              className="px-3 py-1.5 rounded-full text-sm font-medium text-white flex items-center gap-2"
              style={{ backgroundColor: getDomainColor(selectedExpertise) }}
            >
              {selectedExpertise}
              <button 
                onClick={handleClearExpertise}
                className="hover:bg-white/20 rounded-full p-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
            <span className="text-xs text-gray-600 dark:text-gray-400">
              {nodes.filter(n => n.type === 'professor').length} professors
            </span>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="absolute top-4 right-4 flex gap-2 z-10">
        <button
          onClick={handleZoomIn}
          className="p-2 bg-white dark:bg-gray-700 rounded-lg shadow-md hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-5 h-5 text-gray-700 dark:text-gray-300" />
        </button>
        <button
          onClick={handleZoomOut}
          className="p-2 bg-white dark:bg-gray-700 rounded-lg shadow-md hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-5 h-5 text-gray-700 dark:text-gray-300" />
        </button>
        <button
          onClick={handleReset}
          className="p-2 bg-white dark:bg-gray-700 rounded-lg shadow-md hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
          title="Reset View"
        >
          <RotateCcw className="w-5 h-5 text-gray-700 dark:text-gray-300" />
        </button>
        <button
          onClick={onToggleFullscreen}
          className="p-2 bg-white dark:bg-gray-700 rounded-lg shadow-md hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
          title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
        >
          {isFullscreen ? (
            <Minimize2 className="w-5 h-5 text-gray-700 dark:text-gray-300" />
          ) : (
            <Maximize2 className="w-5 h-5 text-gray-700 dark:text-gray-300" />
          )}
        </button>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm p-3 rounded-xl shadow-lg z-10">
        <p className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">Legend</p>
        <div className="flex gap-4 mb-2">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span className="text-xs text-gray-600 dark:text-gray-400">Professor</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-purple-500"></div>
            <span className="text-xs text-gray-600 dark:text-gray-400">Expertise</span>
          </div>
        </div>
        <div className="flex items-center gap-2 mb-2">
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-gray-400"></div>
            <div className="w-3 h-3 rounded-full bg-gray-400"></div>
            <div className="w-4 h-4 rounded-full bg-gray-400"></div>
          </div>
          <span className="text-xs text-gray-600 dark:text-gray-400">Size = Citations</span>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-500">Click expertise to filter • Click professor to view</p>
      </div>

      {/* Hovered node tooltip */}
      {hoveredNode && (
        <div 
          className="absolute bg-white dark:bg-gray-800 px-3 py-2 rounded-lg shadow-xl z-20 pointer-events-none max-w-xs"
          style={{ 
            left: Math.min(hoveredNode.screenX + 10, dimensions.width - 200),
            top: hoveredNode.screenY - 40
          }}
        >
          <p className="font-semibold text-gray-900 dark:text-white text-sm">{hoveredNode.label}</p>
          {hoveredNode.type === 'professor' && (
            <>
              {hoveredNode.data.college && (
                <p className="text-xs text-gray-600 dark:text-gray-400">{hoveredNode.data.college}</p>
              )}
              {hoveredNode.citations > 0 && (
                <p className="text-xs text-blue-600 dark:text-blue-400 font-medium">{hoveredNode.citations} citations</p>
              )}
            </>
          )}
          {hoveredNode.type === 'expertise' && (
            <p className="text-xs text-gray-600 dark:text-gray-400">
              {hoveredNode.professors?.length || 0} professors
            </p>
          )}
        </div>
      )}

      {/* SVG Graph */}
      <svg
        ref={svgRef}
        width={dimensions.width}
        height={dimensions.height}
        className="cursor-grab active:cursor-grabbing"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
      >
        <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
          {/* Links */}
          {visibleLinks.map((link, i) => {
            const sourceNode = nodes.find(n => n.id === link.source);
            const targetNode = nodes.find(n => n.id === link.target);
            if (!sourceNode || !targetNode) return null;
            
            // In filtered mode, show all links prominently
            const linkOpacity = selectedExpertise ? 0.4 : 0.3;
            const linkColor = selectedExpertise ? getDomainColor(selectedExpertise) : '#CBD5E1';
            
            return (
              <line
                key={`link-${i}`}
                x1={sourceNode.x}
                y1={sourceNode.y}
                x2={targetNode.x}
                y2={targetNode.y}
                stroke={linkColor}
                strokeWidth={selectedExpertise ? 1.5 : 1}
                strokeOpacity={linkOpacity}
              />
            );
          })}

          {/* Nodes */}
          {nodes.map((node) => {
            const isConnected = connectedProfessors.has(node.id);
            const shouldFade = false; // Don't fade in filtered mode
            
            if (node.type === 'professor') {
              const nodeSize = node.nodeSize || 8;
              const hasCitations = (node.citations || 0) > 0;
              
              return (
                <g
                  key={node.id}
                  transform={`translate(${node.x}, ${node.y})`}
                  className="cursor-pointer transition-transform hover:scale-110"
                  onClick={() => handleNodeClick(node)}
                  onMouseEnter={(e) => {
                    setHoveredNode({
                      ...node,
                      screenX: (node.x * zoom + pan.x),
                      screenY: (node.y * zoom + pan.y)
                    });
                  }}
                  onMouseLeave={() => setHoveredNode(null)}
                  style={{ opacity: shouldFade ? 0.2 : 1 }}
                >
                  {/* Citation ring for high-cited professors */}
                  {hasCitations && nodeSize > 12 && (
                    <circle
                      r={nodeSize + 4}
                      fill="none"
                      stroke={getDomainColor(node.data.domain_expertise?.split(',')[0])}
                      strokeWidth={2}
                      strokeOpacity={0.3}
                    />
                  )}
                  <circle
                    r={nodeSize}
                    fill={getDomainColor(node.data.domain_expertise?.split(',')[0])}
                    stroke="white"
                    strokeWidth={2}
                    className="drop-shadow-md"
                  />
                  {/* Show name for larger nodes or when zoomed in */}
                  {(zoom > 0.7 || nodeSize > 15) && (
                    <text
                      y={nodeSize + 12}
                      textAnchor="middle"
                      className="fill-gray-700 dark:fill-gray-300 font-medium pointer-events-none"
                      style={{ fontSize: `${Math.max(9, 10 / zoom)}px` }}
                    >
                      {node.label.length > 18 ? node.label.substring(0, 18) + '...' : node.label}
                    </text>
                  )}
                  {/* Show citation count for larger nodes */}
                  {nodeSize > 15 && hasCitations && (
                    <text
                      y={4}
                      textAnchor="middle"
                      className="fill-white font-bold pointer-events-none"
                      style={{ fontSize: `${Math.max(8, nodeSize / 2)}px` }}
                    >
                      {node.citations > 999 ? Math.round(node.citations / 1000) + 'k' : node.citations}
                    </text>
                  )}
                </g>
              );
            } else {
              // Expertise node (central node in filtered mode)
              const isCenter = node.id === 'central-expertise';
              const nodeSize = isCenter ? 50 : Math.max(20, Math.min(40, 15 + (node.professors?.length || 0) * 2));
              
              return (
                <g
                  key={node.id}
                  transform={`translate(${node.x}, ${node.y})`}
                  className="cursor-pointer transition-transform hover:scale-110"
                  onClick={() => handleNodeClick(node)}
                  onMouseEnter={(e) => {
                    setHoveredNode({
                      ...node,
                      screenX: (node.x * zoom + pan.x),
                      screenY: (node.y * zoom + pan.y)
                    });
                  }}
                  onMouseLeave={() => setHoveredNode(null)}
                >
                  <rect
                    x={-nodeSize / 2}
                    y={-nodeSize / 2}
                    width={nodeSize}
                    height={nodeSize}
                    rx={isCenter ? 12 : 6}
                    fill={getDomainColor(node.label)}
                    stroke="white"
                    strokeWidth={isCenter ? 4 : 2}
                    className="drop-shadow-lg"
                  />
                  {/* Expertise label */}
                  <text
                    y={nodeSize / 2 + 14}
                    textAnchor="middle"
                    className="fill-gray-800 dark:fill-gray-200 font-bold pointer-events-none"
                    style={{ fontSize: `${(isCenter ? 13 : 11) / zoom}px` }}
                  >
                    {node.label}
                  </text>
                  {/* Professor count */}
                  <text
                    y={4}
                    textAnchor="middle"
                    className="fill-white font-bold pointer-events-none"
                    style={{ fontSize: `${(isCenter ? 16 : 12) / zoom}px` }}
                  >
                    {node.professors?.length || 0}
                  </text>
                </g>
              );
            }
          })}
        </g>
      </svg>
    </div>
  );
};

const Statistics = ({ onNavigateBack }) => {
  const [professors, setProfessors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProfessor, setSelectedProfessor] = useState(null);
  const [selectedExpertiseArea, setSelectedExpertiseArea] = useState(null);
  const [isGraphFullscreen, setIsGraphFullscreen] = useState(false);
  const [activeView, setActiveView] = useState('graph'); // 'graph' or 'stats'

  // Stats computed from real data
  const [stats, setStats] = useState({
    totalFaculty: 0,
    totalCitations: 0,
    totalPublications: 0,
    departments: 0,
    expertiseDistribution: [],
    topCitedFaculty: [],
    avgHIndex: 0,
    professorsWithScholar: 0
  });

  // Fetch professors data
  useEffect(() => {
    const fetchProfessors = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:5000/api/professors?include_citations=true');
        if (response.ok) {
          const data = await response.json();
          if (data && data.professors) {
            setProfessors(data.professors);
            
            // Calculate statistics from real data
            const totalCitations = data.professors.reduce((sum, p) => sum + (p.citations_count || 0), 0);
            const colleges = new Set(data.professors.map(p => p.college).filter(Boolean));
            
            // Calculate total publications from i10_index (papers with 10+ citations) as a base
            // and estimate total based on typical academic ratios
            const totalI10Index = data.professors.reduce((sum, p) => sum + (p.i10_index || 0), 0);
            const professorsWithPublications = data.professors.filter(p => p.i10_index > 0 || p.h_index > 0).length;
            // Estimate: typically i10-index represents about 30-40% of total publications for active researchers
            const estimatedPublications = totalI10Index > 0 ? Math.round(totalI10Index * 2.5) : professorsWithPublications * 5;
            
            // Calculate average h-index for professors who have one
            const professorsWithHIndex = data.professors.filter(p => p.h_index > 0);
            const avgHIndex = professorsWithHIndex.length > 0 
              ? Math.round(professorsWithHIndex.reduce((sum, p) => sum + p.h_index, 0) / professorsWithHIndex.length)
              : 0;
            
            // Count professors with Google Scholar profiles
            const professorsWithScholar = data.professors.filter(p => 
              p.google_scholar_url || p.has_google_scholar || p.citations_count > 0
            ).length;
            
            // Calculate expertise distribution
            const expertiseCount = {};
            data.professors.forEach(p => {
              if (p.domain_expertise) {
                p.domain_expertise.split(',').forEach(domain => {
                  const d = domain.trim();
                  if (d) {
                    expertiseCount[d] = (expertiseCount[d] || 0) + 1;
                  }
                });
              }
            });
            
            const expertiseDistribution = Object.entries(expertiseCount)
              .sort((a, b) => b[1] - a[1])
              .slice(0, 10)
              .map(([area, count]) => ({
                area,
                count,
                percentage: Math.round((count / data.professors.length) * 100)
              }));

            // Get top cited faculty
            const topCitedFaculty = [...data.professors]
              .filter(p => p.citations_count > 0)
              .sort((a, b) => (b.citations_count || 0) - (a.citations_count || 0))
              .slice(0, 5)
              .map(p => ({
                id: p.id,
                name: p.name,
                citations: p.citations_count || 0,
                hIndex: p.h_index || 0,
                data: p
              }));

            setStats({
              totalFaculty: data.professors.length,
              totalCitations: totalCitations,
              totalPublications: estimatedPublications,
              departments: colleges.size,
              expertiseDistribution,
              topCitedFaculty,
              avgHIndex,
              professorsWithScholar
            });
          }
        } else {
          setError('Failed to fetch professors data');
        }
      } catch (err) {
        console.error('Error fetching professors:', err);
        setError('Failed to connect to the server');
      } finally {
        setLoading(false);
      }
    };

    fetchProfessors();
  }, []);

  // Format large numbers
  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

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
          
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                Faculty Research Statistics
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-400">
                Explore professors, their expertise, and research metrics
              </p>
            </div>
            
            {/* View Toggle */}
            <div className="flex bg-gray-200 dark:bg-gray-700 rounded-xl p-1">
              <button
                onClick={() => setActiveView('graph')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                  activeView === 'graph' 
                    ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-md' 
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                <Network className="w-5 h-5" />
                Knowledge Graph
              </button>
              <button
                onClick={() => setActiveView('stats')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                  activeView === 'stats' 
                    ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-md' 
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                <BarChart3 className="w-5 h-5" />
                Statistics
              </button>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-600 dark:text-gray-400">Loading faculty data...</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6 text-center">
            <p className="text-red-600 dark:text-red-400">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Retry
            </button>
          </div>
        )}

        {/* Main Content */}
        {!loading && !error && (
          <>
            {/* Statistics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Faculty</p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.totalFaculty}</p>
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
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatNumber(stats.totalCitations)}</p>
                  </div>
                  <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-xl flex items-center justify-center">
                    <Award className="w-6 h-6 text-green-600 dark:text-green-400" />
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Est. Publications</p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatNumber(stats.totalPublications)}</p>
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
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.departments}</p>
                  </div>
                  <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-xl flex items-center justify-center">
                    <Building className="w-6 h-6 text-orange-600 dark:text-orange-400" />
                  </div>
                </div>
              </div>
            </div>

            {/* Knowledge Graph View */}
            {activeView === 'graph' && (
              <div className="mb-8">
                <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                  <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                    <div className="flex items-center">
                      <Network className="w-6 h-6 text-blue-600 dark:text-blue-400 mr-3" />
                      <div>
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Professor-Expertise Knowledge Graph</h2>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Interactive visualization of faculty and their research domains</p>
                      </div>
                    </div>
                  </div>
                  <KnowledgeGraph 
                    professors={professors}
                    onSelectProfessor={setSelectedProfessor}
                    isFullscreen={isGraphFullscreen}
                    onToggleFullscreen={() => setIsGraphFullscreen(!isGraphFullscreen)}
                  />
                </div>
              </div>
            )}

            {/* Statistics View */}
            {activeView === 'stats' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* Research Areas Distribution */}
                <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center mb-6">
                    <BarChart3 className="w-6 h-6 text-blue-600 dark:text-blue-400 mr-3" />
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Research Areas Distribution</h2>
                  </div>
                  <div className="space-y-4">
                    {stats.expertiseDistribution.map((item, index) => (
                      <div 
                        key={index} 
                        className="flex items-center justify-between cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-2 rounded-lg transition-colors group"
                        onClick={() => setSelectedExpertiseArea(item.area)}
                      >
                        <div className="flex items-center gap-3">
                          <div 
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: getDomainColor(item.area) }}
                          ></div>
                          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{item.area}</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div 
                              className="h-2 rounded-full transition-all duration-300"
                              style={{ 
                                width: `${Math.min(item.percentage * 2, 100)}%`,
                                backgroundColor: getDomainColor(item.area)
                              }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-600 dark:text-gray-400 w-8">{item.count}</span>
                          <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-blue-500 transition-colors" />
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
                    {stats.topCitedFaculty.length > 0 ? (
                      stats.topCitedFaculty.map((faculty, index) => (
                        <div 
                          key={index} 
                          className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-xl cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                          onClick={() => setSelectedProfessor(faculty.data)}
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold">
                              {index + 1}
                            </div>
                            <div>
                              <p className="font-medium text-gray-900 dark:text-white">{faculty.name}</p>
                              <p className="text-sm text-gray-600 dark:text-gray-400">h-index: {faculty.hIndex}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="font-bold text-blue-600 dark:text-blue-400">{formatNumber(faculty.citations)}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">citations</p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-gray-500 dark:text-gray-400 text-center py-4">
                        No citation data available
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Quick Access - Professors by Expertise */}
            {activeView === 'stats' && (
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Browse by Expertise</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Click on any expertise area to see all professors</p>
                <div className="flex flex-wrap gap-2">
                  {stats.expertiseDistribution.map((item, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedExpertiseArea(item.area)}
                      className="px-4 py-2 rounded-full text-sm font-medium text-white transition-transform hover:scale-105"
                      style={{ backgroundColor: getDomainColor(item.area) }}
                    >
                      {item.area} ({item.count})
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Additional Stats */}
            {activeView === 'stats' && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl shadow-lg p-6 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-blue-100">Avg. h-index</p>
                      <p className="text-3xl font-bold">{stats.avgHIndex}</p>
                    </div>
                    <Award className="w-10 h-10 text-blue-200" />
                  </div>
                  <p className="text-xs text-blue-200 mt-2">Among faculty with citations</p>
                </div>

                <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl shadow-lg p-6 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-purple-100">Scholar Profiles</p>
                      <p className="text-3xl font-bold">{stats.professorsWithScholar}</p>
                    </div>
                    <BookOpen className="w-10 h-10 text-purple-200" />
                  </div>
                  <p className="text-xs text-purple-200 mt-2">{Math.round((stats.professorsWithScholar / stats.totalFaculty) * 100)}% of faculty</p>
                </div>

                <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl shadow-lg p-6 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-green-100">Research Areas</p>
                      <p className="text-3xl font-bold">{Object.keys(stats.expertiseDistribution).length}+</p>
                    </div>
                    <Network className="w-10 h-10 text-green-200" />
                  </div>
                  <p className="text-xs text-green-200 mt-2">Unique expertise domains</p>
                </div>
              </div>
            )}
          </>
        )}

        {/* Profile Modal */}
        {selectedProfessor && (
          <ProfileModal 
            professor={selectedProfessor} 
            onClose={() => setSelectedProfessor(null)} 
          />
        )}

        {/* Expertise List Modal */}
        {selectedExpertiseArea && (
          <ExpertiseListModal
            expertise={selectedExpertiseArea}
            professors={professors}
            onClose={() => setSelectedExpertiseArea(null)}
            onSelectProfessor={setSelectedProfessor}
          />
        )}
      </div>
    </div>
  );
};

export default Statistics;