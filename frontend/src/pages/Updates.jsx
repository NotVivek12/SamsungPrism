import React, { useState, useEffect } from 'react';
import { CheckCircle, Bell } from 'lucide-react';
import { ArrowLeft, UserCircle, Mail, Info, Paperclip, X } from 'lucide-react';

const Updates = () => {
  const [updates, setUpdates] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Mock data to simulate fetching updates about completed worklets
  const mockUpdates = [
    {
      id: 1,
      type: 'completed',
      title: 'Dr. Jane Doe: "AI in Climate Modeling" Worklet Complete',
      message: 'The worklet focused on developing a predictive AI model for climate change has been successfully completed. The model is now available for use by the research team.',
      timestamp: '2 hours ago',
    },
    {
      id: 2,
      type: 'completed',
      title: 'Professor Alex Chen: "Robotics Ethics Framework" Worklet Complete',
      message: 'Professor Chen has finalized the worklet on establishing an ethical framework for autonomous systems. The guidelines are now integrated into ongoing robotics projects.',
      timestamp: '1 day ago',
    },
    {
      id: 3,
      type: 'completed',
      title: 'Dr. Emily White: "Quantum Computing Algorithms" Worklet Complete',
      message: 'The worklet for creating new algorithms for a quantum simulator is finished. This research is expected to contribute to a new publication.',
      timestamp: '3 days ago',
    },
    {
      id: 4,
      type: 'completed',
      title: 'Professor David Lee: "Sustainable Materials Analysis" Worklet Complete',
      message: 'Professor Lee has completed the worklet on analyzing the durability of sustainable composites. The findings will be used in the new infrastructure development project.',
      timestamp: '1 week ago',
    },
  ];

  // Simulate data fetching on component mount
  useEffect(() => {
    setIsLoading(true);
    // In a real application, this would be an API call
    setTimeout(() => {
      setUpdates(mockUpdates);
      setIsLoading(false);
    }, 500);
  }, []);

  // Helper function to get icon based on update type
  const getIcon = (type) => {
    switch (type) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />;
      default:
        return <CheckCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-50 dark:bg-slate-900">
        <div className="text-xl font-semibold text-gray-600 dark:text-slate-400">
          Loading updates...
        </div>
      </div>
    );
  }

  return (
    <div className="flex-wrap h-[75vh] overflow-y-scroll bg-slate-50 p-8 dark:bg-slate-900 dark:text-slate-200 max-w-7xl">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-3xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-purple-600 flex items-center gap-2">
          <Bell className="w-8 h-8 text-blue-600 dark:text-blue-400" /> New Updates
        </h2>
        <p className="text-gray-600 mb-8 dark:text-slate-400">
          This page shows notifications about professors' completed worklets and other significant progress.
        </p>

        {updates.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-xl shadow-md dark:bg-slate-800">
            <p className="text-gray-500 dark:text-slate-400">No new updates at this time.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {updates.map((update) => (
              <div
                key={update.id}
                className="flex items-start bg-white p-6 rounded-xl shadow-md transition-shadow hover:shadow-lg duration-200 dark:bg-slate-800"
              >
                <div className="flex-shrink-0 mt-1 mr-4">
                  {getIcon(update.type)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {update.title}
                    </h3>
                    <span className="text-sm text-gray-500 dark:text-slate-400">
                      {update.timestamp}
                    </span>
                  </div>
                  <p className="mt-2 text-gray-700 dark:text-slate-300">
                    {update.message}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Updates;