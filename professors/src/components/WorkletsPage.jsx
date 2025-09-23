import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { 
  Calendar, 
  Users, 
  Home
} from "lucide-react";

// --- IMPORT DATA FROM THE NEW FILE ---
import { STATUS_OPTIONS, SAMPLE_WORKLETS, statusIcons } from "./data";

export default function WorkletsPage() {
  const location = useLocation();
  const workletsData = location.state?.workletsData || SAMPLE_WORKLETS;
  const [activeTab, setActiveTab] = useState("Ongoing");
  const [isHoverActive, setIsHoverActive] = useState(false);

  const filteredWorklets = workletsData.filter(
    (w) => w.status === activeTab
  );

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200">
      {/* --- SIDEBAR --- */}
      <nav 
        className="w-20 bg-white dark:bg-gray-800 dark:border-r dark:border-gray-700 shadow-md flex flex-col z-20"
        onMouseEnter={() => setIsHoverActive(true)}
        onMouseLeave={() => setIsHoverActive(false)}
      >
        <div className="h-20 flex items-center justify-center">
            <div className="w-12 h-12 flex items-center justify-center rounded-lg">
                <img src="https://play-lh.googleusercontent.com/e8F34JODgtXalC7mK09QocqhT5QCqDBPRPclFZmkcWZFc_oy2FCpofb5AFdyG_1hdg=w480-h960-rw" alt="Prism" className="object-contain"/>
            </div>
        </div>
        <div className="flex-grow flex flex-col items-center justify-center space-y-4 w-full">
          <Link
            to="/home"
            className="relative w-full h-12 flex justify-center items-center text-gray-500 hover:text-indigo-600 dark:text-gray-400 dark:hover:text-indigo-400 transition-colors"
          >
            <Home size={27} />
            {isHoverActive && (
              <div className="absolute left-full top-0 h-full flex items-center pl-4 pr-8 bg-gradient-to-r from-white via-white/95 to-transparent dark:from-gray-800 dark:via-gray-800/95 dark:to-transparent rounded-r-lg shadow-sm animate-fade-in-right pointer-events-none">
                <span className="text-gray-800 dark:text-gray-200 font-medium whitespace-nowrap">Home</span>
              </div>
            )}
          </Link>
          <div className="w-full space-y-2">
            {STATUS_OPTIONS.map((status) => (
              <button
                key={status}
                onClick={() => setActiveTab(status)}
                className={`relative w-full h-12 flex justify-center items-center rounded-lg transition-all duration-200 ${
                  activeTab === status
                    ? "bg-indigo-50 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-400"
                    : "text-gray-500 hover:text-indigo-600 dark:text-gray-400 dark:hover:text-indigo-400"
                }`}
              >
                {statusIcons[status]}
                {isHoverActive && (
                  <div className="absolute left-full top-0 h-full flex items-center pl-4 pr-8 bg-gradient-to-r from-white via-white/95 to-transparent dark:from-gray-800 dark:via-gray-800/95 dark:to-transparent rounded-r-lg shadow-sm animate-fade-in-right pointer-events-none">
                    <span className="text-gray-800 dark:text-gray-200 font-medium whitespace-nowrap">{status}</span>
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>
        <div className="h-20"></div>
      </nav>

      {/* --- MAIN CONTENT AREA --- */}
      <main className="flex-1 p-8 overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4 text-blue-900 dark:text-blue-400">{activeTab} Worklets</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredWorklets.length > 0 ? (
            filteredWorklets.map((worklet) => (
              <Link to={`/worklet/${worklet.id}`} key={worklet.id}>
                <div className="bg-white dark:bg-gray-800 dark:border dark:border-gray-700 rounded-xl shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden group h-full">
                  <img src={worklet.imageUrl} alt={worklet.title} className="h-40 w-full object-cover group-hover:scale-105 transition-transform duration-300"/>
                  <div className="p-5">
                    <h3 className="font-bold text-lg text-gray-900 dark:text-gray-100 truncate">{worklet.title}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 h-10 overflow-hidden">{worklet.description}</p>
                    <div className="mt-4 flex justify-between items-center text-xs text-gray-500 dark:text-gray-400">
                      <span className="flex items-center gap-1.5"><Calendar size={14}/> {worklet.startDate} - {worklet.endDate}</span>
                      <span className="font-semibold">{worklet.progress}%</span>
                    </div>
                    <div className="mt-2 h-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full">
                      <div className="h-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full" style={{width: `${worklet.progress}%`}}></div>
                    </div>
                    <div className="mt-4">
                      <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300"><Users size={16}/> Assigned Students</div>
                      <ul className="mt-2 list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1">
                        {worklet.students.map((student) => (<li key={student}>{student}</li>))}
                      </ul>
                    </div>
                  </div>
                </div>
              </Link>
            ))
          ) : (
            <div className="col-span-full text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">No worklets found for "{activeTab}".</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}