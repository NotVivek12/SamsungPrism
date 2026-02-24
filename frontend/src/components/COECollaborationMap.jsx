import React, { useState, useMemo } from 'react';
import { ResponsiveChord } from '@nivo/chord';
import { Users, Zap, AlertTriangle, Crown, ChevronDown, ChevronUp, ExternalLink, X, Sparkles, TrendingUp, Link2 } from 'lucide-react';

// ─── Samsung COE Definitions ───────────────────────────────────────────────
const COE_DEFINITIONS = [
    { name: 'IoT', icon: '🌐', color: '#10B981', gradient: 'from-emerald-500 to-teal-600', keywords: ['iot', 'internet of things', 'sensor network', 'embedded system', 'wsn', 'smart city', 'manet', 'ad hoc', 'ad-hoc', 'edge computing', 'edgeai', 'cyber physical', 'smart antenna', 'biomedical instrumentation', 'biosensor', 'virtual instrumentation'] },
    { name: 'Multimedia', icon: '🎬', color: '#EC4899', gradient: 'from-pink-500 to-rose-600', keywords: ['multimedia', 'video coding', 'image processing', 'digital image', 'graphics', 'ar/vr', 'augmented reality', 'virtual reality', 'game development', '3d', 'steganography', 'remote sensing', 'medical image', 'image retrieval', 'image classification', 'object recognition', 'pattern recognition', 'medical imaging', 'biosignal processing', 'signal processing'] },
    { name: 'On-device AI', icon: '🧠', color: '#8B5CF6', gradient: 'from-violet-500 to-purple-600', keywords: ['machine learning', 'deep learning', 'artificial intelligence', 'neural network', ' ai', 'ai ', 'ai/', '/ai', 'ai&', '&ai', ' ml', 'ml ', 'cnn', 'soft computing', 'fuzzy', 'genetic algorithm', 'optimization', 'data mining', 'data analytics', 'data science', 'federated learning', 'neuromorphic', 'continual learning', 'agentic ai', 'few-shot', 'predictive analysis', 'anomaly detection', 'medical ai'] },
    { name: 'Vision', icon: '👁️', color: '#F59E0B', gradient: 'from-amber-500 to-orange-600', keywords: ['computer vision', 'object recognition', 'image classification', 'biometric', 'face', 'pattern recognition', 'image processing', 'medical imaging', 'image retrieval'] },
    { name: 'Voice', icon: '🎙️', color: '#06B6D4', gradient: 'from-cyan-500 to-blue-600', keywords: ['speech', 'voice', 'nlp', 'natural language', 'text mining', 'speaker recognition', 'spoken language', 'speech signal', 'machine translation'] },
    { name: 'Network', icon: '📡', color: '#3B82F6', gradient: 'from-blue-500 to-indigo-600', keywords: ['network', '5g', '6g', 'wireless', 'communication', 'protocol', 'mimo', 'ofdm', 'gfdm', 'sdn', 'routing', 'fso', 'mmwave', 'vehicular', 'congestion', 'manets', 'vanets'] },
    { name: 'Cloud', icon: '☁️', color: '#0EA5E9', gradient: 'from-sky-500 to-blue-500', keywords: ['cloud', 'distributed system', 'parallel computing', 'high performance computing', 'fog', 'web service', 'soa', 'microservice', 'distributed algorithm', 'grid computing', 'operating system'] },
    { name: 'Adv. Research', icon: '🔬', color: '#64748B', gradient: 'from-slate-500 to-gray-600', keywords: ['blockchain', 'cryptography', 'security', 'quantum', 'robotics', 'bioinformatics', 'computational biology', 'biomedical', 'bioelectronics', 'formal method', 'automata', 'compiler', 'vlsi', 'semiconductor', 'digital forensic'] }
];

// ─── Utility: Map a professor to COE indices ───────────────────────────────
function getProfessorCOEs(professor) {
    const expertise = (professor.domain_expertise || '').toLowerCase();
    const indices = [];
    COE_DEFINITIONS.forEach((coe, i) => {
        if (coe.keywords.some(kw => expertise.includes(kw))) {
            indices.push(i);
        }
    });
    return indices;
}

// ─── Build chord matrix + metadata from professors ─────────────────────────
function buildCollaborationData(professors) {
    const n = COE_DEFINITIONS.length;
    // Matrix: matrix[i][j] = number of professors shared between COE i and COE j
    const matrix = Array.from({ length: n }, () => Array(n).fill(0));
    // Bridge professors: bridgeMap[i][j] = array of shared professors
    const bridgeMap = Array.from({ length: n }, () => Array.from({ length: n }, () => []));
    // Per-professor COE membership
    const professorCOECount = [];

    professors.forEach(prof => {
        const coes = getProfessorCOEs(prof);
        professorCOECount.push({ professor: prof, coeCount: coes.length, coeIndices: coes });

        // For every pair of COEs this professor belongs to, increment the matrix
        for (let a = 0; a < coes.length; a++) {
            for (let b = a + 1; b < coes.length; b++) {
                const i = coes[a], j = coes[b];
                matrix[i][j] += 1;
                matrix[j][i] += 1;
                bridgeMap[i][j].push(prof);
                bridgeMap[j][i].push(prof);
            }
        }
        // Self-loop: professors only in one COE (adds weight to diagonal for visual balance)
        if (coes.length === 1) {
            matrix[coes[0]][coes[0]] += 1;
        }
    });

    // Find collaboration gaps (COE pairs with 0 shared professors, excluding self)
    const gaps = [];
    const strongPairs = [];
    for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
            if (matrix[i][j] === 0) {
                gaps.push({ coe1: COE_DEFINITIONS[i], coe2: COE_DEFINITIONS[j], idx1: i, idx2: j });
            } else {
                strongPairs.push({
                    coe1: COE_DEFINITIONS[i],
                    coe2: COE_DEFINITIONS[j],
                    count: matrix[i][j],
                    professors: bridgeMap[i][j],
                    idx1: i,
                    idx2: j
                });
            }
        }
    }
    strongPairs.sort((a, b) => b.count - a.count);

    // Super connectors: professors in 4+ COEs
    const superConnectors = professorCOECount
        .filter(p => p.coeCount >= 3)
        .sort((a, b) => b.coeCount - a.coeCount)
        .slice(0, 10);

    return { matrix, bridgeMap, gaps, strongPairs, superConnectors };
}

// ─── Format numbers ─────────────────────────────────────────────────────────
const formatNum = (n) => {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return n.toString();
};

// ─── Bridge Professors Panel ────────────────────────────────────────────────
function BridgeProfessorsPanel({ pair, onClose, onSelectProfessor }) {
    const sortedProfs = [...pair.professors].sort((a, b) => (b.citations_count || 0) - (a.citations_count || 0));

    return (
        <div
            className="rounded-2xl border border-gray-200 dark:border-gray-700 shadow-2xl overflow-hidden"
            style={{ animation: 'fadeSlideUp 0.4s ease-out' }}
        >
            {/* Header */}
            <div className={`bg-gradient-to-r ${pair.coe1.gradient} p-5 text-white relative overflow-hidden`}>
                <div className="absolute inset-0 bg-black/10"></div>
                <div className="relative flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center">
                            <span className="text-3xl">{pair.coe1.icon}</span>
                            <Link2 className="w-6 h-6 mx-3 text-white/70" />
                            <span className="text-3xl">{pair.coe2.icon}</span>
                        </div>
                        <div>
                            <h3 className="text-xl font-bold">
                                {pair.coe1.name} ↔ {pair.coe2.name}
                            </h3>
                            <p className="text-white/80 text-sm">
                                {pair.count} bridge professors connecting these centers
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-10 h-10 bg-white/20 hover:bg-white/30 rounded-xl flex items-center justify-center transition-colors backdrop-blur-sm"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>
            </div>

            {/* Professor List */}
            <div className="bg-white dark:bg-gray-800">
                <div className="grid grid-cols-12 px-6 py-3 bg-gray-50 dark:bg-gray-750 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 border-b border-gray-100 dark:border-gray-700">
                    <div className="col-span-1">#</div>
                    <div className="col-span-3">Professor</div>
                    <div className="col-span-5">Domain Expertise</div>
                    <div className="col-span-1 text-center">Citations</div>
                    <div className="col-span-1 text-center">h-index</div>
                    <div className="col-span-1 text-center">View</div>
                </div>
                <div className="max-h-[400px] overflow-y-auto">
                    {sortedProfs.map((prof, idx) => (
                        <div
                            key={prof.id || idx}
                            className="grid grid-cols-12 px-6 py-3.5 items-center hover:bg-blue-50/50 dark:hover:bg-gray-700/50 cursor-pointer transition-all duration-200 border-b border-gray-50 dark:border-gray-700/50"
                            onClick={() => onSelectProfessor(prof)}
                        >
                            <div className="col-span-1">
                                <span className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${idx < 3
                                        ? `bg-gradient-to-br ${pair.coe1.gradient} text-white shadow-md`
                                        : 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                                    }`}>
                                    {idx + 1}
                                </span>
                            </div>
                            <div className="col-span-3">
                                <p className="font-semibold text-gray-900 dark:text-white text-sm">{prof.name}</p>
                                <p className="text-xs text-gray-400 dark:text-gray-500 truncate">{prof.college || ''}</p>
                            </div>
                            <div className="col-span-5">
                                <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 leading-relaxed">{prof.domain_expertise || 'N/A'}</p>
                            </div>
                            <div className="col-span-1 text-center">
                                <span className="font-bold text-blue-600 dark:text-blue-400 text-sm">{formatNum(prof.citations_count || 0)}</span>
                            </div>
                            <div className="col-span-1 text-center">
                                <span className="font-medium text-gray-700 dark:text-gray-300 text-sm">{prof.h_index || '—'}</span>
                            </div>
                            <div className="col-span-1 text-center">
                                <button
                                    onClick={(e) => { e.stopPropagation(); onSelectProfessor(prof); }}
                                    className="text-blue-500 hover:text-blue-700 dark:text-blue-400 transition-colors"
                                >
                                    <ExternalLink className="w-4 h-4 inline" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

// ─── Main Component ─────────────────────────────────────────────────────────
export default function COECollaborationMap({ professors, onSelectProfessor }) {
    const [selectedPair, setSelectedPair] = useState(null);
    const [showAllPairs, setShowAllPairs] = useState(false);
    const [hoveredRibbon, setHoveredRibbon] = useState(null);

    // Compute all data
    const { matrix, bridgeMap, gaps, strongPairs, superConnectors } = useMemo(
        () => buildCollaborationData(professors || []),
        [professors]
    );

    const coeNames = COE_DEFINITIONS.map(c => c.name);
    const coeColors = COE_DEFINITIONS.map(c => c.color);

    // Handle ribbon click on the chord diagram
    const handleRibbonClick = (ribbon) => {
        const sourceIdx = ribbon.source.index;
        const targetIdx = ribbon.target.index;
        if (sourceIdx === targetIdx) return; // skip self-loops
        const i = Math.min(sourceIdx, targetIdx);
        const j = Math.max(sourceIdx, targetIdx);
        const profs = bridgeMap[i][j];
        if (profs.length > 0) {
            setSelectedPair({
                coe1: COE_DEFINITIONS[i],
                coe2: COE_DEFINITIONS[j],
                count: profs.length,
                professors: profs,
                idx1: i,
                idx2: j
            });
        }
    };

    // Total cross-domain connections
    const totalConnections = strongPairs.reduce((s, p) => s + p.count, 0);

    const visiblePairs = showAllPairs ? strongPairs : strongPairs.slice(0, 5);

    return (
        <div className="space-y-8">
            {/* ━━━ Section Header ━━━ */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <div className="w-14 h-14 bg-gradient-to-br from-violet-500 via-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-lg shadow-purple-200 dark:shadow-purple-900/30">
                            <Zap className="w-7 h-7 text-white" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                                Cross-COE Collaboration Intelligence
                            </h2>
                            <p className="text-gray-500 dark:text-gray-400 text-sm mt-0.5">
                                Discover interdisciplinary bridges between Centers of Excellence
                            </p>
                        </div>
                    </div>
                    <div className="flex flex-wrap gap-3">
                        <div className="flex items-center gap-2 bg-violet-50 dark:bg-violet-900/30 px-4 py-2.5 rounded-xl">
                            <Link2 className="w-4 h-4 text-violet-600 dark:text-violet-400" />
                            <span className="font-bold text-violet-700 dark:text-violet-300">{strongPairs.length}</span>
                            <span className="text-violet-600 dark:text-violet-400 text-sm">Active corridors</span>
                        </div>
                        <div className="flex items-center gap-2 bg-amber-50 dark:bg-amber-900/30 px-4 py-2.5 rounded-xl">
                            <Users className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                            <span className="font-bold text-amber-700 dark:text-amber-300">{totalConnections}</span>
                            <span className="text-amber-600 dark:text-amber-400 text-sm">Bridge researchers</span>
                        </div>
                        {gaps.length > 0 && (
                            <div className="flex items-center gap-2 bg-red-50 dark:bg-red-900/30 px-4 py-2.5 rounded-xl">
                                <AlertTriangle className="w-4 h-4 text-red-500 dark:text-red-400" />
                                <span className="font-bold text-red-600 dark:text-red-300">{gaps.length}</span>
                                <span className="text-red-500 dark:text-red-400 text-sm">Gaps identified</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* ━━━ Chord Diagram ━━━ */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                <div className="p-5 border-b border-gray-100 dark:border-gray-700">
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                        <span className="font-medium text-gray-700 dark:text-gray-300">Interactive:</span>{' '}
                        Click any ribbon to see the bridge professors connecting two COEs. Hover for details.
                    </p>
                </div>
                <div className="relative" style={{ height: 520 }}>
                    <ResponsiveChord
                        data={matrix}
                        keys={coeNames}
                        margin={{ top: 40, right: 40, bottom: 40, left: 40 }}
                        valueFormat=".0f"
                        padAngle={0.04}
                        innerRadiusRatio={0.9}
                        innerRadiusOffset={0.02}
                        arcOpacity={1}
                        arcBorderWidth={2}
                        arcBorderColor={{ from: 'color', modifiers: [['darker', 0.6]] }}
                        ribbonOpacity={0.55}
                        ribbonBorderWidth={1}
                        ribbonBorderColor={{ from: 'color', modifiers: [['darker', 0.6]] }}
                        ribbonBlendMode="multiply"
                        enableLabel={true}
                        label="id"
                        labelOffset={14}
                        labelRotation={-90}
                        labelTextColor={{ from: 'color', modifiers: [['darker', 1.4]] }}
                        colors={coeColors}
                        motionConfig="gentle"
                        isInteractive={true}
                        arcHoverOpacity={1}
                        arcHoverOthersOpacity={0.25}
                        ribbonHoverOpacity={0.85}
                        ribbonHoverOthersOpacity={0.15}
                        onRibbonClick={handleRibbonClick}
                        tooltipFormat={(value) => `${value} shared professors`}
                        layers={['ribbons', 'arcs', 'labels', 'legends']}
                    />
                    {/* Center label */}
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <div className="text-center">
                            <p className="text-3xl font-black text-gray-900 dark:text-white">{totalConnections}</p>
                            <p className="text-xs font-medium text-gray-400 dark:text-gray-500 uppercase tracking-widest">Bridge<br />Researchers</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* ━━━ Bridge Professors Panel (on click) ━━━ */}
            {selectedPair && (
                <BridgeProfessorsPanel
                    pair={selectedPair}
                    onClose={() => setSelectedPair(null)}
                    onSelectProfessor={onSelectProfessor}
                />
            )}

            {/* ━━━ Two-column: Strongest Corridors + Collaboration Gaps ━━━ */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Strongest Corridors */}
                <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                    <div className="p-5 border-b border-gray-100 dark:border-gray-700 flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                            <TrendingUp className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Strongest Research Corridors</h3>
                            <p className="text-xs text-gray-500 dark:text-gray-400">COE pairs ranked by shared professors</p>
                        </div>
                    </div>
                    <div className="divide-y divide-gray-50 dark:divide-gray-700/50">
                        {visiblePairs.map((pair, idx) => {
                            const maxCount = strongPairs[0]?.count || 1;
                            const percentage = Math.round((pair.count / maxCount) * 100);
                            return (
                                <div
                                    key={`${pair.idx1}-${pair.idx2}`}
                                    className="flex items-center gap-4 px-5 py-4 hover:bg-blue-50/40 dark:hover:bg-gray-700/30 cursor-pointer transition-all duration-200 group"
                                    onClick={() => setSelectedPair(pair)}
                                >
                                    <span className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold ${idx < 3
                                            ? 'bg-gradient-to-br from-amber-400 to-orange-500 text-white shadow-md'
                                            : 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                                        }`}>
                                        {idx + 1}
                                    </span>

                                    <div className="flex items-center gap-2 min-w-[180px]">
                                        <span className="text-lg">{pair.coe1.icon}</span>
                                        <span className="text-xs text-gray-400">↔</span>
                                        <span className="text-lg">{pair.coe2.icon}</span>
                                        <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">
                                            {pair.coe1.name} — {pair.coe2.name}
                                        </span>
                                    </div>

                                    <div className="flex-1">
                                        <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2.5 overflow-hidden">
                                            <div
                                                className="h-full rounded-full transition-all duration-500"
                                                style={{
                                                    width: `${percentage}%`,
                                                    background: `linear-gradient(90deg, ${pair.coe1.color}, ${pair.coe2.color})`
                                                }}
                                            />
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-2">
                                        <span className="font-bold text-blue-600 dark:text-blue-400 text-lg min-w-[30px] text-right">
                                            {pair.count}
                                        </span>
                                        <span className="text-xs text-gray-400 dark:text-gray-500">shared</span>
                                        <ChevronDown className="w-4 h-4 text-gray-300 group-hover:text-blue-500 transition-colors" />
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                    {strongPairs.length > 5 && (
                        <div className="p-4 border-t border-gray-100 dark:border-gray-700">
                            <button
                                onClick={() => setShowAllPairs(!showAllPairs)}
                                className="w-full text-center text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors flex items-center justify-center gap-1"
                            >
                                {showAllPairs ? (
                                    <><ChevronUp className="w-4 h-4" /> Show less</>
                                ) : (
                                    <><ChevronDown className="w-4 h-4" /> Show all {strongPairs.length} corridors</>
                                )}
                            </button>
                        </div>
                    )}
                </div>

                {/* Collaboration Gaps + Super Connectors */}
                <div className="space-y-6">
                    {/* Gaps */}
                    {gaps.length > 0 && (
                        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-red-100 dark:border-red-900/30 overflow-hidden">
                            <div className="p-5 border-b border-red-50 dark:border-red-900/20 flex items-center gap-3">
                                <div className="w-10 h-10 bg-gradient-to-br from-red-400 to-rose-500 rounded-xl flex items-center justify-center">
                                    <AlertTriangle className="w-5 h-5 text-white" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">Collaboration Gaps</h3>
                                    <p className="text-xs text-red-500 dark:text-red-400">No shared researchers — hiring opportunities</p>
                                </div>
                            </div>
                            <div className="p-4 space-y-3">
                                {gaps.map((gap, idx) => (
                                    <div
                                        key={idx}
                                        className="flex items-center justify-between p-3 bg-red-50/50 dark:bg-red-900/10 rounded-xl border border-red-100/50 dark:border-red-900/20"
                                    >
                                        <div className="flex items-center gap-2">
                                            <span className="text-lg">{gap.coe1.icon}</span>
                                            <span className="text-red-300 dark:text-red-700 text-xs font-mono">✕</span>
                                            <span className="text-lg">{gap.coe2.icon}</span>
                                        </div>
                                        <span className="text-xs font-medium text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/30 px-2.5 py-1 rounded-full">
                                            Gap
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Super Connectors */}
                    {superConnectors.length > 0 && (
                        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-amber-100 dark:border-amber-900/30 overflow-hidden">
                            <div className="p-5 border-b border-amber-50 dark:border-amber-900/20 flex items-center gap-3">
                                <div className="w-10 h-10 bg-gradient-to-br from-amber-400 to-yellow-500 rounded-xl flex items-center justify-center shadow-md shadow-amber-200 dark:shadow-amber-900/30">
                                    <Crown className="w-5 h-5 text-white" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">Super Connectors</h3>
                                    <p className="text-xs text-amber-600 dark:text-amber-400">Professors spanning 3+ COEs</p>
                                </div>
                            </div>
                            <div className="p-4 space-y-2">
                                {superConnectors.slice(0, 7).map((sc, idx) => (
                                    <div
                                        key={idx}
                                        className="flex items-center justify-between p-3 rounded-xl hover:bg-amber-50/50 dark:hover:bg-gray-700/30 cursor-pointer transition-all group"
                                        onClick={() => onSelectProfessor(sc.professor)}
                                    >
                                        <div className="flex items-center gap-3 min-w-0">
                                            <span className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${idx === 0
                                                    ? 'bg-gradient-to-br from-amber-400 to-yellow-500 text-white shadow-md'
                                                    : idx < 3
                                                        ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300'
                                                        : 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                                                }`}>
                                                {idx + 1}
                                            </span>
                                            <div className="min-w-0">
                                                <p className="text-sm font-semibold text-gray-900 dark:text-white truncate group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                                                    {sc.professor.name}
                                                </p>
                                                <div className="flex items-center gap-1 mt-0.5 flex-wrap">
                                                    {sc.coeIndices.map(ci => (
                                                        <span key={ci} className="text-xs" title={COE_DEFINITIONS[ci].name}>
                                                            {COE_DEFINITIONS[ci].icon}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="text-right flex-shrink-0 ml-2">
                                            <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-gradient-to-r from-amber-100 to-yellow-100 dark:from-amber-900/30 dark:to-yellow-900/30 rounded-full">
                                                <Sparkles className="w-3 h-3 text-amber-600 dark:text-amber-400" />
                                                <span className="text-xs font-bold text-amber-700 dark:text-amber-300">{sc.coeCount} COEs</span>
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* ━━━ CSS Animation ━━━ */}
            <style>{`
        @keyframes fadeSlideUp {
          from { opacity: 0; transform: translateY(16px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
        </div>
    );
}
