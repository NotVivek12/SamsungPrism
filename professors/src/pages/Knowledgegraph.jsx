import React, { useState } from 'react';
import { UserCircle, GraduationCap, Paperclip, Lightbulb } from 'lucide-react';

const Knowledgegraph = () => {
  // Mock data for the knowledge graph nodes and links
  const mockNodes = [
    { id: 'p1', type: 'person', label: 'Dr. Evelyn Reed', role: 'Professor', icon: <UserCircle size={32} /> },
    { id: 't1', type: 'topic', label: 'AI Ethics', icon: <Lightbulb size={24} /> },
    { id: 't2', type: 'topic', label: 'Robotics', icon: <Lightbulb size={24} /> },
    { id: 't3', type: 'topic', label: 'Machine Learning', icon: <Lightbulb size={24} /> },
    { id: 'pub1', type: 'publication', label: 'Autonomous Systems', icon: <Paperclip size={24} /> },
    { id: 'pub2', type: 'publication', label: 'Ethical AI', icon: <Paperclip size={24} /> },
    { id: 'proj1', type: 'project', label: 'Project Sentinel', icon: <GraduationCap size={24} /> },
  ];

  const mockLinks = [
    { source: 'p1', target: 't1', type: 'researches' },
    { source: 'p1', target: 't2', type: 'teaches' },
    { source: 'p1', target: 't3', type: 'researches' },
    { source: 'p1', target: 'pub1', type: 'published' },
    { source: 'p1', target: 'pub2', type: 'published' },
    { source: 'p1', target: 'proj1', type: 'leads' },
    { source: 't1', target: 'pub2', type: 'covered_in' },
    { source: 't2', target: 'pub1', type: 'covered_in' },
    { source: 't3', target: 'pub1', type: 'covered_in' },
  ];

  const [activeNode, setActiveNode] = useState(null);

  const nodePositions = {
    p1: 'top-[40%] left-[40%]',
    t1: 'top-[15%] left-[20%]',
    t2: 'top-[10%] left-[60%]',
    t3: 'top-[70%] left-[10%]',
    pub1: 'top-[35%] right-[10%]',
    pub2: 'top-[80%] left-[45%]',
    proj1: 'top-[60%] right-[30%]',
  };

  const nodeStyles = {
    person: 'bg-blue-600 dark:bg-blue-500',
    topic: 'bg-green-600 dark:bg-green-500',
    publication: 'bg-purple-600 dark:bg-purple-500',
    project: 'bg-yellow-600 dark:bg-yellow-500',
  };

  const handleNodeClick = (node) => {
    setActiveNode(node);
  };

  return (
    <div className="flex-wrap h-[75vh] overflow-y-scroll bg-slate-50 p-4 dark:bg-slate-900 dark:text-slate-200">
      <div className="max-w-7xl mx-auto h-full flex flex-col">
        <h1 className="text-3xl font-bold mb-3 text-blue-900 dark:text-white">
          Interactive Knowledge Graph
        </h1>
        <p className="text-sm text-gray-500 dark:text-slate-400 mb-6">
          Explore the interconnected network of faculty, research topics, and projects.
        </p>

        <div className="flex-1 relative w-full bg-white rounded-xl shadow-lg border border-gray-200 dark:bg-slate-800 dark:border-slate-700 overflow-hidden">
          {/* Static Links - CSS lines to simulate connections */}
          <div className="absolute w-[18%] h-[2px] bg-gray-400 dark:bg-gray-600 top-[48%] left-[27%] transform -rotate-45 origin-left"></div>
          <div className="absolute w-[20%] h-[2px] bg-gray-400 dark:bg-gray-600 top-[28%] left-[40%] transform -rotate-[70deg] origin-left"></div>
          <div className="absolute w-[30%] h-[2px] bg-gray-400 dark:bg-gray-600 top-[35%] left-[24%] transform rotate-15 origin-left"></div>
          <div className="absolute w-[28%] h-[2px] bg-gray-400 dark:bg-gray-600 top-[45%] left-[50%] transform rotate-10 origin-left"></div>
          <div className="absolute w-[25%] h-[2px] bg-gray-400 dark:bg-gray-600 top-[55%] left-[30%] transform rotate-[70deg] origin-left"></div>
          <div className="absolute w-[15%] h-[2px] bg-gray-400 dark:bg-gray-600 top-[70%] right-[38%] transform rotate-15 origin-right"></div>
          <div className="absolute w-[15%] h-[2px] bg-gray-400 dark:bg-gray-600 top-[60%] right-[35%] transform -rotate-30 origin-right"></div>

          {/* Nodes */}
          {mockNodes.map(node => (
            <div
              key={node.id}
              onClick={() => handleNodeClick(node)}
              className={`absolute flex flex-col items-center justify-center p-3 rounded-full transition-all duration-300 transform hover:scale-110 cursor-pointer text-white shadow-xl ${nodePositions[node.id]} ${nodeStyles[node.type]}`}
            >
              {node.icon}
              <span className="mt-1 font-semibold text-xs text-center">{node.label}</span>
              {node.type === 'person' && <span className="text-[9px] opacity-80">{node.role}</span>}
            </div>
          ))}
        </div>

        {/* Node Details Panel */}
        <div className="mt-4 p-4 rounded-xl bg-white shadow-md dark:bg-slate-800">
          <h2 className="text-xl font-bold mb-2 text-blue-800 dark:text-blue-400">Node Details</h2>
          {activeNode ? (
            <div>
              <p className="text-lg font-semibold">{activeNode.label}</p>
              <p className="text-sm text-gray-500 dark:text-slate-400 mt-1">Type: <span className="capitalize">{activeNode.type}</span></p>
              <p className="mt-2 text-sm text-gray-700 dark:text-slate-300">
                This is a placeholder for detailed information about **{activeNode.label}**. In a real application, this panel would display a biography, research interests, associated publications, and other relevant data.
              </p>
            </div>
          ) : (
            <p className="text-sm text-gray-500 dark:text-slate-400">Click on a node in the graph to view its details.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Knowledgegraph;