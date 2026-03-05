import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ResponsiveSunburst } from '@nivo/sunburst';
import { ArrowLeft, Search, X, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';

// Transform professor data into hierarchical Sunburst format
const transformToHierarchy = (professors) => {
    if (!professors || professors.length === 0) {
        return { name: 'Research', children: [] };
    }

    const domainMap = new Map();

    professors.forEach((prof) => {
        const domains = prof.domain_expertise
            ? prof.domain_expertise.split(',').map(d => d.trim()).filter(d => d)
            : ['General'];

        domains.forEach((domain) => {
            if (!domainMap.has(domain)) {
                domainMap.set(domain, []);
            }
            domainMap.get(domain).push({
                name: prof.name || 'Unknown',
                value: prof.citations_count || 10, // Use citations for sizing
                professor: prof
            });
        });
    });

    const children = Array.from(domainMap.entries()).map(([domain, profs]) => ({
        name: domain,
        children: profs
    }));

    return {
        name: 'Research',
        children: children
    };
};

export default function ResearchDashboard() {
    const navigate = useNavigate();
    const [professors, setProfessors] = useState([]);
    const [hierarchyData, setHierarchyData] = useState({ name: 'Research', children: [] });
    const [filteredData, setFilteredData] = useState({ name: 'Research', children: [] });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedNode, setSelectedNode] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [zoomLevel, setZoomLevel] = useState(1);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/professors?include_citations=true');
                if (!response.ok) throw new Error('Failed to fetch data');

                const data = await response.json();

                // Extract professors array from response
                const professorsList = data.professors || [];
                setProfessors(professorsList);

                const hierarchy = transformToHierarchy(professorsList);
                setHierarchyData(hierarchy);
                setFilteredData(hierarchy);
                setLoading(false);
            } catch (err) {
                setError(err.message);
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    // Filter data based on search query
    useEffect(() => {
        if (!searchQuery.trim()) {
            setFilteredData(hierarchyData);
            return;
        }

        const query = searchQuery.toLowerCase();
        const filtered = {
            name: 'Research',
            children: hierarchyData.children
                .map(domain => ({
                    ...domain,
                    children: domain.children.filter(prof =>
                        prof.name.toLowerCase().includes(query) ||
                        domain.name.toLowerCase().includes(query)
                    )
                }))
                .filter(domain => domain.children.length > 0)
        };

        setFilteredData(filtered);
    }, [searchQuery, hierarchyData]);

    const handleZoomIn = () => setZoomLevel(prev => Math.min(prev + 0.2, 2));
    const handleZoomOut = () => setZoomLevel(prev => Math.max(prev - 0.2, 0.5));
    const handleReset = () => {
        setZoomLevel(1);
        setSearchQuery('');
        setSelectedNode(null);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-gray-600 dark:text-gray-400">Loading research data...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 max-w-md w-full">
                    <div className="text-red-500 text-6xl mb-4 text-center">⚠️</div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 text-center">Failed to load data</h2>
                    <p className="text-gray-600 dark:text-gray-400 text-center mb-6">{error}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-4 md:p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <button
                        onClick={() => navigate('/')}
                        className="flex items-center text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 mb-6 font-medium transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5 mr-2" />
                        Back to Home
                    </button>

                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                        <div>
                            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                                Research Insights Dashboard
                            </h1>
                            <p className="text-gray-600 dark:text-gray-400">
                                Explore {professors.length} professors across research domains
                            </p>
                        </div>
                    </div>
                </div>

                {/* Search and Controls */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
                    <div className="flex flex-col md:flex-row gap-4">
                        {/* Search Bar */}
                        <div className="flex-1 relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                            <input
                                type="text"
                                placeholder="Search by professor name or research domain..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full pl-10 pr-10 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                            {searchQuery && (
                                <button
                                    onClick={() => setSearchQuery('')}
                                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            )}
                        </div>

                        {/* Zoom Controls */}
                        <div className="flex gap-2">
                            <button
                                onClick={handleZoomOut}
                                className="p-3 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
                                title="Zoom Out"
                            >
                                <ZoomOut className="w-5 h-5 text-gray-700 dark:text-gray-300" />
                            </button>
                            <button
                                onClick={handleZoomIn}
                                className="p-3 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
                                title="Zoom In"
                            >
                                <ZoomIn className="w-5 h-5 text-gray-700 dark:text-gray-300" />
                            </button>
                            <button
                                onClick={handleReset}
                                className="p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                                title="Reset View"
                            >
                                <RotateCcw className="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    {/* Stats */}
                    {searchQuery && (
                        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Found {filteredData.children.reduce((acc, domain) => acc + domain.children.length, 0)} professors
                                in {filteredData.children.length} domains matching "{searchQuery}"
                            </p>
                        </div>
                    )}
                </div>

                {/* Sunburst Chart */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                    <div style={{ height: `${600 * zoomLevel}px`, minHeight: '500px' }}>
                        <ResponsiveSunburst
                            data={filteredData}
                            margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
                            id="name"
                            value="value"
                            cornerRadius={3}
                            borderWidth={2}
                            borderColor={{ from: 'color', modifiers: [['darker', 0.3]] }}
                            colors={{ scheme: 'nivo' }}
                            childColor={{ from: 'color', modifiers: [['brighter', 0.13]] }}
                            enableArcLabels={true}
                            arcLabel={(d) => d.id}
                            arcLabelsSkipAngle={15}
                            arcLabelsTextColor="#ffffff"
                            arcLabelsRadiusOffset={0.5}
                            onClick={(node) => setSelectedNode(node)}
                            tooltip={({ id, value, color, data }) => (
                                <div className="bg-gray-900 text-white px-4 py-3 rounded-lg shadow-xl border border-gray-700 max-w-xs">
                                    <div className="flex items-center gap-2 mb-2">
                                        <div
                                            className="w-4 h-4 rounded-full"
                                            style={{ backgroundColor: color }}
                                        />
                                        <strong className="text-lg">{id}</strong>
                                    </div>
                                    {value && (
                                        <p className="text-sm text-gray-300">
                                            {value.toLocaleString()} citations
                                        </p>
                                    )}
                                    {data.professor && (
                                        <div className="mt-2 pt-2 border-t border-gray-700 text-sm">
                                            <p className="text-gray-400">Click for details</p>
                                        </div>
                                    )}
                                </div>
                            )}
                            theme={{
                                labels: {
                                    text: {
                                        fontSize: 14,
                                        fontWeight: 600,
                                        fill: '#ffffff',
                                        outlineWidth: 2,
                                        outlineColor: '#000000'
                                    }
                                },
                                tooltip: {
                                    container: {
                                        background: '#1f2937',
                                        fontSize: '14px'
                                    }
                                }
                            }}
                        />
                    </div>
                </div>

                {/* Selected Node Details */}
                {selectedNode && selectedNode.data && selectedNode.data.professor && (
                    <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                        <div className="flex items-start justify-between mb-4">
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                                {selectedNode.data.professor.name}
                            </h3>
                            <button
                                onClick={() => setSelectedNode(null)}
                                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                            >
                                <X className="w-6 h-6" />
                            </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Domain Expertise</p>
                                <p className="text-gray-900 dark:text-white font-medium">
                                    {selectedNode.data.professor.domain_expertise || 'N/A'}
                                </p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Citations</p>
                                <p className="text-gray-900 dark:text-white font-medium">
                                    {selectedNode.data.professor.citations_count?.toLocaleString() || 'N/A'}
                                </p>
                            </div>
                            {selectedNode.data.professor.college && (
                                <div>
                                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">College</p>
                                    <p className="text-gray-900 dark:text-white font-medium">
                                        {selectedNode.data.professor.college}
                                    </p>
                                </div>
                            )}
                            {selectedNode.data.professor.email && (
                                <div>
                                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Email</p>
                                    <a
                                        href={`mailto:${selectedNode.data.professor.email}`}
                                        className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
                                    >
                                        {selectedNode.data.professor.email}
                                    </a>
                                </div>
                            )}
                        </div>

                        {selectedNode.data.professor.google_scholar_url && (
                            <div className="mt-4">
                                <a
                                    href={selectedNode.data.professor.google_scholar_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline"
                                >
                                    View Google Scholar Profile →
                                </a>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
