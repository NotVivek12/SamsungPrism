import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';
import {
  Search, X, ZoomIn, ZoomOut, RotateCcw, Maximize2, Minimize2,
  Download, ChevronRight, ChevronDown, Layers, GitBranch, 
  User, BookOpen, Award, ExternalLink, Mail, Building
} from 'lucide-react';

// Register dagre layout
cytoscape.use(dagre);

// Node type colors
const nodeColors = {
  Field: '#8B5CF6',      // Purple
  Subfield: '#3B82F6',   // Blue
  Skill: '#10B981',      // Green
  Person: '#F59E0B',     // Amber
  default: '#6B7280'     // Gray
};

// Get color for a node type
const getNodeColor = (type) => nodeColors[type] || nodeColors.default;

// Cytoscape stylesheet
const cytoscapeStylesheet = [
  {
    selector: 'node',
    style: {
      'label': 'data(label)',
      'text-valign': 'bottom',
      'text-halign': 'center',
      'font-size': '11px',
      'font-weight': 500,
      'text-margin-y': 8,
      'text-wrap': 'ellipsis',
      'text-max-width': '120px',
      'color': '#374151',
      'text-outline-color': '#ffffff',
      'text-outline-width': 2,
      'min-zoomed-font-size': 8,
    }
  },
  {
    selector: 'node[type="Field"]',
    style: {
      'background-color': 'data(color)',  // Use field-specific color from data
      'width': 70,
      'height': 70,
      'shape': 'round-rectangle',
      'border-width': 4,
      'border-color': '#5B21B6',
      'font-size': '14px',
      'font-weight': 700,
      'text-margin-y': 10,
    }
  },
  {
    selector: 'node[type="Subfield"]',
    style: {
      'background-color': nodeColors.Subfield,
      'width': 50,
      'height': 50,
      'shape': 'round-rectangle',
      'border-width': 3,
      'border-color': '#1D4ED8',
      'font-size': '11px',
      'font-weight': 600,
    }
  },
  {
    selector: 'node[type="Skill"]',
    style: {
      'background-color': nodeColors.Skill,
      'width': 30,
      'height': 30,
      'shape': 'ellipse',
      'border-width': 2,
      'border-color': '#059669',
      'font-size': '10px',
    }
  },
  {
    selector: 'node[type="Person"]',
    style: {
      'background-color': nodeColors.Person,
      'width': 35,
      'height': 35,
      'shape': 'ellipse',
      'border-width': 2,
      'border-color': '#D97706',
    }
  },
  {
    selector: 'node:selected',
    style: {
      'border-width': 4,
      'border-color': '#EF4444',
      'overlay-color': '#EF4444',
      'overlay-opacity': 0.2,
    }
  },
  {
    selector: 'node.highlighted',
    style: {
      'border-width': 4,
      'border-color': '#EF4444',
      'z-index': 999,
    }
  },
  {
    selector: 'node.faded',
    style: {
      'opacity': 0.3,
    }
  },
  {
    selector: 'node.collapsed',
    style: {
      'background-opacity': 0.7,
    }
  },
  {
    selector: 'edge',
    style: {
      'width': 2,
      'line-color': '#CBD5E1',
      'target-arrow-color': '#94A3B8',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      'arrow-scale': 0.8,
    }
  },
  {
    selector: 'edge[relation="HAS_SUBFIELD"]',
    style: {
      'line-color': '#8B5CF6',
      'target-arrow-color': '#8B5CF6',
      'width': 3,
    }
  },
  {
    selector: 'edge[relation="HAS_MEMBER"]',
    style: {
      'line-color': '#3B82F6',
      'target-arrow-color': '#3B82F6',
      'width': 2,
    }
  },
  {
    selector: 'edge[relation="HAS_SKILL"]',
    style: {
      'line-color': '#10B981',
      'target-arrow-color': '#10B981',
    }
  },
  {
    selector: 'edge[relation="RELATED_TO"]',
    style: {
      'line-color': '#F59E0B',
      'target-arrow-color': '#F59E0B',
      'line-style': 'dashed',
    }
  },
  {
    selector: 'edge.faded',
    style: {
      'opacity': 0.2,
    }
  },
  {
    selector: 'edge.highlighted',
    style: {
      'width': 3,
      'z-index': 999,
    }
  }
];

/**
 * Map canonical JSON-LD to Cytoscape elements
 */
export function mapToCytoscapeElements(graphJson, collapsedNodes = new Set()) {
  const nodes = [];
  const edges = [];

  function walk(node, parentId = null, depth = 0) {
    const nodeId = node.id;
    const isCollapsed = collapsedNodes.has(nodeId);

    nodes.push({
      data: {
        id: nodeId,
        label: node.label,
        type: node.type,
        description: node.description || '',
        color: node.color || getNodeColor(node.type),
        hasChildren: Array.isArray(node.children) && node.children.length > 0,
        childCount: node.children?.length || 0,
        isCollapsed,
        depth,
        // Additional data for persons
        citations: node.citations,
        hIndex: node.hIndex,
        i10Index: node.i10Index,
        email: node.email,
        college: node.college,
        scholarUrl: node.scholarUrl,
        profilePicture: node.profilePicture,
        profileLink: node.profileLink,
        domainExpertise: node.domainExpertise,
        phdThesis: node.phdThesis,
        // Store original professor data for opening profile modal
        professorData: node.professorData,
        // For field nodes
        professorCount: node.professorCount,
        totalCitations: node.totalCitations,
      },
      classes: isCollapsed ? 'collapsed' : '',
    });

    if (parentId) {
      // Determine edge relationship based on parent-child types
      let relation;
      if (node.type === 'Person') {
        relation = 'HAS_MEMBER';  // Subfield -> Person
      } else if (node.type === 'Subfield') {
        relation = 'HAS_SUBFIELD';  // Field -> Subfield
      } else if (node.type === 'Skill') {
        relation = 'HAS_SKILL';
      } else {
        relation = 'HAS_CHILD';
      }
      edges.push({
        data: {
          id: `${parentId}->${nodeId}`,
          source: parentId,
          target: nodeId,
          relation,
        }
      });
    }

    // Only add children if not collapsed
    if (!isCollapsed && Array.isArray(node.children)) {
      node.children.forEach(child => walk(child, nodeId, depth + 1));
    }
  }

  // Handle @graph array or direct array
  const graphNodes = graphJson['@graph'] || graphJson;
  if (Array.isArray(graphNodes)) {
    graphNodes.forEach(root => walk(root, null, 0));
  }

  // Add relationship edges (RELATED_TO links between fields)
  if (graphJson.relationships && Array.isArray(graphJson.relationships)) {
    graphJson.relationships.forEach(rel => {
      edges.push({
        data: {
          id: `${rel.source}->${rel.target}-rel`,
          source: rel.source,
          target: rel.target,
          relation: rel.type || 'RELATED_TO',
          label: rel.label,
        }
      });
    });
  }

  return { nodes, edges };
}

/**
 * Node Detail Side Panel
 */
const NodeDetailPanel = ({ node, onClose, onViewProfile }) => {
  if (!node) return null;

  const data = node.data();
  const TypeIcon = data.type === 'Person' ? User : 
                   data.type === 'Field' ? Layers : 
                   data.type === 'Subfield' ? GitBranch : BookOpen;

  return (
    <div className="absolute right-4 top-4 bottom-4 w-80 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden flex flex-col z-30">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-start justify-between">
        <div className="flex items-center gap-3">
          {data.type === 'Person' && data.profilePicture ? (
            <img 
              src={data.profilePicture} 
              alt={data.label}
              className="w-12 h-12 rounded-full object-cover border-2 border-amber-500"
            />
          ) : (
            <div 
              className="w-10 h-10 rounded-lg flex items-center justify-center text-white"
              style={{ backgroundColor: data.color || getNodeColor(data.type) }}
            >
              <TypeIcon className="w-5 h-5" />
            </div>
          )}
          <div>
            <h3 className="font-bold text-gray-900 dark:text-white text-lg">{data.label}</h3>
            <span 
              className="text-xs px-2 py-0.5 rounded-full text-white"
              style={{ backgroundColor: data.color || getNodeColor(data.type) }}
            >
              {data.type}
            </span>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {/* Person-specific info */}
        {data.type === 'Person' && (
          <>
            {/* View Profile Button */}
            <button
              onClick={() => onViewProfile && onViewProfile(data)}
              className="w-full mb-4 px-4 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium hover:from-blue-600 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
            >
              <User className="w-5 h-5" />
              View Full Profile
            </button>

            {data.college && (
              <div className="mb-3 flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <Building className="w-4 h-4" />
                {data.college}
              </div>
            )}
            {data.email && (
              <a 
                href={`mailto:${data.email}`}
                className="mb-3 flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 hover:underline"
              >
                <Mail className="w-4 h-4" />
                {data.email}
              </a>
            )}

            {/* Domain Expertise */}
            {data.domainExpertise && (
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Expertise</h4>
                <div className="flex flex-wrap gap-1">
                  {data.domainExpertise.split(',').slice(0, 5).map((domain, i) => (
                    <span 
                      key={i}
                      className="px-2 py-0.5 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-full text-xs"
                    >
                      {domain.trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Citation metrics */}
            {(data.citations > 0 || data.hIndex > 0 || data.i10Index > 0) && (
              <div className="mb-4 grid grid-cols-3 gap-2">
                {data.citations > 0 && (
                  <div className="bg-blue-50 dark:bg-blue-900/20 p-2 rounded-xl text-center">
                    <p className="text-lg font-bold text-blue-600 dark:text-blue-400">{data.citations}</p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">Citations</p>
                  </div>
                )}
                {data.hIndex > 0 && (
                  <div className="bg-purple-50 dark:bg-purple-900/20 p-2 rounded-xl text-center">
                    <p className="text-lg font-bold text-purple-600 dark:text-purple-400">{data.hIndex}</p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">h-index</p>
                  </div>
                )}
                {data.i10Index > 0 && (
                  <div className="bg-green-50 dark:bg-green-900/20 p-2 rounded-xl text-center">
                    <p className="text-lg font-bold text-green-600 dark:text-green-400">{data.i10Index}</p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">i10-index</p>
                  </div>
                )}
              </div>
            )}

            {/* Research Description */}
            {data.description && (
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Research Interests</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-3">{data.description}</p>
              </div>
            )}

            {/* Links */}
            <div className="flex flex-col gap-2">
              {data.scholarUrl && (
                <a
                  href={data.scholarUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 px-4 py-2 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors text-sm"
                >
                  <ExternalLink className="w-4 h-4" />
                  Google Scholar
                </a>
              )}
              {data.profileLink && (
                <a
                  href={data.profileLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 px-4 py-2 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-lg hover:bg-purple-200 dark:hover:bg-purple-900/50 transition-colors text-sm"
                >
                  <ExternalLink className="w-4 h-4" />
                  University Profile
                </a>
              )}
            </div>
          </>
        )}

        {/* Field-specific info */}
        {data.type === 'Field' && (
          <>
            <div className="mb-4 grid grid-cols-2 gap-3">
              <div className="bg-purple-50 dark:bg-purple-900/20 p-3 rounded-xl text-center">
                <p className="text-xl font-bold text-purple-600 dark:text-purple-400">{data.professorCount || data.childCount || 0}</p>
                <p className="text-xs text-gray-600 dark:text-gray-400">Professors</p>
              </div>
              {data.totalCitations > 0 && (
                <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-xl text-center">
                  <p className="text-xl font-bold text-blue-600 dark:text-blue-400">{data.totalCitations}</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">Total Citations</p>
                </div>
              )}
            </div>
            {data.isCollapsed && (
              <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
                Double-click to expand and see professors
              </p>
            )}
          </>
        )}

        {/* Description for non-person nodes */}
        {data.type !== 'Person' && data.description && (
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Description</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">{data.description}</p>
          </div>
        )}

        {/* Children info */}
        {data.hasChildren && data.type !== 'Field' && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">Child nodes:</span>
              <span className="font-semibold text-gray-900 dark:text-white">{data.childCount}</span>
            </div>
            {data.isCollapsed && (
              <p className="mt-2 text-xs text-gray-500">Double-click to expand</p>
            )}
          </div>
        )}

        {/* Hierarchy info */}
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Hierarchy</h4>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Depth: {data.depth}
          </p>
        </div>
      </div>
    </div>
  );
};

/**
 * Legend Component
 */
const Legend = () => (
  <div className="absolute bottom-4 left-4 bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm p-4 rounded-xl shadow-lg z-10 border border-gray-200 dark:border-gray-700">
    <p className="text-xs font-bold text-gray-700 dark:text-gray-300 mb-3">Node Types</p>
    <div className="space-y-2">
      {Object.entries(nodeColors).filter(([key]) => key !== 'default').map(([type, color]) => (
        <div key={type} className="flex items-center gap-2">
          <div 
            className={`w-4 h-4 ${type === 'Field' || type === 'Subfield' ? 'rounded' : 'rounded-full'}`}
            style={{ backgroundColor: color }}
          />
          <span className="text-xs text-gray-600 dark:text-gray-400">{type}</span>
        </div>
      ))}
    </div>
    <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
      <p className="text-xs text-gray-500 dark:text-gray-500">
        Click: Select • Double-click: Expand/Collapse
      </p>
    </div>
  </div>
);

/**
 * Main Knowledge Graph Component
 */
const StatisticsKnowledgeGraph = ({ 
  onSelectProfessor,
  isFullscreen = false,
  onToggleFullscreen 
}) => {
  const cyRef = useRef(null);
  const containerRef = useRef(null);
  
  // State
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [collapsedNodes, setCollapsedNodes] = useState(new Set());
  const [layoutType, setLayoutType] = useState('dagre'); // 'dagre', 'breadthfirst', 'cose'
  const [showLayoutMenu, setShowLayoutMenu] = useState(false);

  // Fetch knowledge graph data - use dynamic source with actual professor data
  useEffect(() => {
    const fetchGraphData = async () => {
      try {
        setLoading(true);
        // Fetch dynamic graph built from actual professor data
        const response = await fetch('http://localhost:5000/api/knowledge-graph?source=dynamic');
        
        if (!response.ok) {
          throw new Error('Failed to fetch knowledge graph');
        }
        
        const data = await response.json();
        setGraphData(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching knowledge graph:', err);
        // Try loading local fallback
        try {
          const fallbackResponse = await fetch('/data/knowledge-graph.example.json');
          if (fallbackResponse.ok) {
            const fallbackData = await fallbackResponse.json();
            setGraphData(fallbackData);
            setError(null);
          } else {
            setError('Failed to load knowledge graph data');
          }
        } catch {
          setError('Failed to load knowledge graph data');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchGraphData();
  }, []);

  // Map data to Cytoscape elements
  const elements = useMemo(() => {
    if (!graphData) return [];
    const { nodes, edges } = mapToCytoscapeElements(graphData, collapsedNodes);
    return [...nodes, ...edges];
  }, [graphData, collapsedNodes]);

  // Layout configuration
  const layoutConfig = useMemo(() => {
    switch (layoutType) {
      case 'dagre':
        return {
          name: 'dagre',
          rankDir: 'TB',           // Top to Bottom hierarchy
          nodeSep: 80,             // Increased horizontal separation
          rankSep: 120,            // Increased vertical separation between levels
          edgeSep: 40,
          padding: 60,
          ranker: 'tight-tree',    // Better hierarchy algorithm
          animate: true,
          animationDuration: 500,
          fit: true,               // Fit graph to viewport
          spacingFactor: 1.2,      // Extra spacing
        };
      case 'breadthfirst':
        return {
          name: 'breadthfirst',
          directed: true,
          padding: 60,
          spacingFactor: 2.0,       // Increased spacing
          animate: true,
          animationDuration: 500,
          circle: false,           // Use tree layout, not circle
          grid: false,
          roots: 'node[type="Field"]', // Start from Field nodes
        };
      case 'cose':
        return {
          name: 'cose',
          idealEdgeLength: 150,
          nodeOverlap: 40,
          refresh: 20,
          fit: true,
          padding: 60,
          animate: true,
          animationDuration: 500,
          gravity: 0.4,
          nodeRepulsion: 8000,
        };
      default:
        return { name: 'dagre', rankDir: 'TB' };
    }
  }, [layoutType]);

  // Debounced search
  useEffect(() => {
    if (!searchQuery.trim() || !cyRef.current) {
      setSearchResults([]);
      cyRef.current?.elements().removeClass('faded highlighted');
      return;
    }

    const timeoutId = setTimeout(() => {
      const cy = cyRef.current;
      const query = searchQuery.toLowerCase();
      
      // Find matching nodes
      const matches = cy.nodes().filter(node => {
        const label = node.data('label')?.toLowerCase() || '';
        const desc = node.data('description')?.toLowerCase() || '';
        return label.includes(query) || desc.includes(query);
      });

      setSearchResults(matches.map(n => ({
        id: n.id(),
        label: n.data('label'),
        type: n.data('type'),
      })));

      // Highlight matching nodes
      cy.elements().addClass('faded');
      matches.removeClass('faded').addClass('highlighted');
      matches.connectedEdges().removeClass('faded').addClass('highlighted');

      // Center on first match if any
      if (matches.length > 0) {
        cy.animate({
          center: { eles: matches.first() },
          zoom: 1.2,
          duration: 300,
        });
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  // Handle node click
  const handleNodeClick = useCallback((node) => {
    setSelectedNode(node);
    
    // If it's a person node and we have a callback, open their profile
    const data = node.data();
    if (data.type === 'Person' && onSelectProfessor) {
      // Use the stored professorData if available, otherwise construct from node data
      const professorData = data.professorData || {
        id: data.id.replace('person-', ''),
        name: data.label,
        email: data.email,
        college: data.college,
        citations_count: data.citations,
        h_index: data.hIndex,
        i10_index: data.i10Index,
        google_scholar_url: data.scholarUrl,
        profile_picture_url: data.profilePicture,
        profile_link: data.profileLink,
        domain_expertise: data.domainExpertise,
        research_interests: data.description,
        phd_thesis: data.phdThesis,
      };
      onSelectProfessor(professorData);
    }
  }, [onSelectProfessor]);

  // Handle double-click to expand/collapse
  const handleNodeDoubleClick = useCallback((node) => {
    const nodeId = node.id();
    const hasChildren = node.data('hasChildren');
    
    if (!hasChildren) return;

    setCollapsedNodes(prev => {
      const next = new Set(prev);
      if (next.has(nodeId)) {
        next.delete(nodeId);
      } else {
        next.add(nodeId);
      }
      return next;
    });
  }, []);

  // Cytoscape initialization callback
  const handleCyInit = useCallback((cy) => {
    cyRef.current = cy;

    // Single click - select node
    cy.on('tap', 'node', (evt) => {
      handleNodeClick(evt.target);
    });

    // Double click - expand/collapse
    cy.on('dbltap', 'node', (evt) => {
      handleNodeDoubleClick(evt.target);
    });

    // Background click - deselect
    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        setSelectedNode(null);
        cy.elements().removeClass('faded highlighted');
      }
    });

    // Run initial layout
    cy.layout(layoutConfig).run();
  }, [handleNodeClick, handleNodeDoubleClick, layoutConfig]);

  // Re-run layout when elements or layout type changes
  useEffect(() => {
    if (cyRef.current && elements.length > 0) {
      cyRef.current.layout(layoutConfig).run();
    }
  }, [elements, layoutConfig]);

  // Zoom controls
  const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.2);
  const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() / 1.2);
  const handleReset = () => {
    cyRef.current?.fit();
    cyRef.current?.elements().removeClass('faded highlighted');
    setSearchQuery('');
    setSelectedNode(null);
  };

  // Export functions
  const handleExportPNG = () => {
    if (!cyRef.current) return;
    const png = cyRef.current.png({ full: true, scale: 2, bg: '#ffffff' });
    const link = document.createElement('a');
    link.download = 'knowledge-graph.png';
    link.href = png;
    link.click();
  };

  const handleExportJSON = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/knowledge-graph/export?format=jsonld');
      const data = await response.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.download = 'knowledge-graph.json';
      link.href = url;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  // Focus on search result
  const handleSearchResultClick = (result) => {
    const cy = cyRef.current;
    if (!cy) return;
    
    const node = cy.getElementById(result.id);
    if (node) {
      cy.animate({
        center: { eles: node },
        zoom: 1.5,
        duration: 300,
      });
      handleNodeClick(node);
    }
    setSearchQuery('');
  };

  if (loading) {
    return (
      <div className={`flex items-center justify-center ${isFullscreen ? 'fixed inset-0 z-50' : 'h-[600px]'} bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-slate-800 rounded-2xl`}>
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading knowledge graph...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex items-center justify-center ${isFullscreen ? 'fixed inset-0 z-50' : 'h-[600px]'} bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-slate-800 rounded-2xl`}>
        <div className="text-center text-red-600 dark:text-red-400">
          <p className="mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-100 dark:bg-red-900/30 rounded-lg hover:bg-red-200"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      className={`relative ${isFullscreen ? 'fixed inset-0 z-50' : 'h-[600px]'} bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-slate-800 rounded-2xl overflow-hidden`}
    >
      {/* Search Bar */}
      <div className="absolute top-4 left-4 z-20 w-80">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search nodes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-10 py-2.5 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl text-gray-900 dark:text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none shadow-lg text-sm"
            aria-label="Search knowledge graph nodes"
          />
          {searchQuery && (
            <button
              onClick={() => {
                setSearchQuery('');
                cyRef.current?.elements().removeClass('faded highlighted');
              }}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-full"
              aria-label="Clear search"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>
          )}
        </div>

        {/* Search Results Dropdown */}
        {searchResults.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl shadow-xl max-h-64 overflow-y-auto">
            {searchResults.slice(0, 10).map((result) => (
              <button
                key={result.id}
                onClick={() => handleSearchResultClick(result)}
                className="w-full px-4 py-2.5 text-left hover:bg-gray-100 dark:hover:bg-gray-600 flex items-center gap-2 first:rounded-t-xl last:rounded-b-xl"
              >
                <div 
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: getNodeColor(result.type) }}
                />
                <span className="text-sm text-gray-900 dark:text-white flex-1">{result.label}</span>
                <span className="text-xs text-gray-500">{result.type}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="absolute top-4 right-4 flex gap-2 z-20">
        {/* Layout Menu */}
        <div className="relative">
          <button
            onClick={() => setShowLayoutMenu(!showLayoutMenu)}
            className="p-2 bg-white dark:bg-gray-700 rounded-lg shadow-md hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            title="Change Layout"
          >
            <Layers className="w-5 h-5 text-gray-700 dark:text-gray-300" />
          </button>
          {showLayoutMenu && (
            <div className="absolute right-0 top-full mt-1 bg-white dark:bg-gray-700 rounded-lg shadow-xl border border-gray-200 dark:border-gray-600 overflow-hidden min-w-32">
              {['dagre', 'breadthfirst', 'cose'].map((layout) => (
                <button
                  key={layout}
                  onClick={() => {
                    setLayoutType(layout);
                    setShowLayoutMenu(false);
                  }}
                  className={`w-full px-4 py-2 text-left text-sm capitalize hover:bg-gray-100 dark:hover:bg-gray-600 ${
                    layoutType === layout ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600' : 'text-gray-700 dark:text-gray-300'
                  }`}
                >
                  {layout === 'dagre' ? 'Hierarchical' : layout === 'cose' ? 'Force-Directed' : 'Breadth-First'}
                </button>
              ))}
            </div>
          )}
        </div>

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
        
        {/* Export Menu */}
        <div className="relative group">
          <button
            className="p-2 bg-white dark:bg-gray-700 rounded-lg shadow-md hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            title="Export"
          >
            <Download className="w-5 h-5 text-gray-700 dark:text-gray-300" />
          </button>
          <div className="absolute right-0 top-full mt-1 bg-white dark:bg-gray-700 rounded-lg shadow-xl border border-gray-200 dark:border-gray-600 overflow-hidden min-w-32 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
            <button
              onClick={handleExportPNG}
              className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600"
            >
              Export PNG
            </button>
            <button
              onClick={handleExportJSON}
              className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600"
            >
              Export JSON
            </button>
          </div>
        </div>

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
      <Legend />

      {/* Node Detail Panel */}
      {selectedNode && (
        <NodeDetailPanel 
          node={selectedNode} 
          onClose={() => setSelectedNode(null)}
          onViewProfile={(data) => {
            // Construct professor data and trigger the profile modal
            const professorData = data.professorData || {
              id: data.id?.replace('person-', ''),
              name: data.label,
              email: data.email,
              college: data.college,
              citations_count: data.citations,
              h_index: data.hIndex,
              i10_index: data.i10Index,
              google_scholar_url: data.scholarUrl,
              profile_picture_url: data.profilePicture,
              scholar_profile_picture: data.profilePicture,
              profile_link: data.profileLink,
              domain_expertise: data.domainExpertise,
              research_interests: data.description,
              phd_thesis: data.phdThesis,
            };
            if (onSelectProfessor) {
              onSelectProfessor(professorData);
            }
          }}
        />
      )}

      {/* Cytoscape Graph */}
      <CytoscapeComponent
        elements={elements}
        stylesheet={cytoscapeStylesheet}
        style={{ width: '100%', height: '100%' }}
        cy={handleCyInit}
        wheelSensitivity={0.2}
        minZoom={0.2}
        maxZoom={3}
        boxSelectionEnabled={false}
      />
    </div>
  );
};

export default StatisticsKnowledgeGraph;
