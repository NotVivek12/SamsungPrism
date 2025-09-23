import React from "react";
import { useParams, Link } from "react-router-dom";
import { SAMPLE_WORKLETS } from "./data"; // Import data
import { Calendar, Users, ArrowLeft } from "lucide-react";

export default function WorkletDetailPage() {
  // Get the 'id' from the URL, e.g., "/worklet/1" -> id is "1"
  const { id } = useParams();
  
  // Find the worklet with the matching id.
  // Note: useParams returns a string, so we convert it to a number.
  const worklet = SAMPLE_WORKLETS.find((w) => w.id === parseInt(id));

  // Handle case where no worklet is found for the given id
  if (!worklet) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-slate-50 dark:bg-gray-900">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Worklet Not Found</h2>
        <Link to="/home" className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600">
          Go Back Home
        </Link>
      </div>
    );
  }

  return (
    <div className="bg-slate-50 dark:bg-gray-900 min-h-screen p-4 sm:p-6 md:p-8">
      <div className="max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden">
        {/* Back Button */}
        <div className="p-4">
          <Link to="/worklets" className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300 font-semibold">
            <ArrowLeft size={20} />
            Back to All Worklets
          </Link>
        </div>
        
        <img src={worklet.imageUrl} alt={worklet.title} className="w-full h-64 object-cover" />
        
        <div className="p-6 md:p-8">
          {/* Header */}
          <span className="text-sm font-semibold text-indigo-600 bg-indigo-100 dark:text-indigo-300 dark:bg-indigo-500/20 px-3 py-1 rounded-full">{worklet.status}</span>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-gray-100 mt-3">{worklet.title}</h1>
          <p className="text-md text-gray-600 dark:text-gray-400 mt-2">{worklet.description}</p>
          
          {/* Dates */}
          <div className="mt-6 flex items-center gap-2 text-gray-500 dark:text-gray-400">
            <Calendar size={18} />
            <span>{worklet.startDate} to {worklet.endDate}</span>
          </div>

          {/* Progress Bar */}
          <div className="mt-6">
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Progress</span>
              <span className="text-sm font-bold text-indigo-600 dark:text-indigo-400">{worklet.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
              <div className="bg-indigo-600 h-2.5 rounded-full" style={{ width: `${worklet.progress}%` }}></div>
            </div>
          </div>
          
          {/* Students */}
          <div className="mt-8">
            <h2 className="flex items-center gap-2 text-xl font-bold text-gray-800 dark:text-gray-200">
              <Users size={22} />
              Assigned Students
            </h2>
            <ul className="mt-3 list-disc list-inside bg-slate-50 dark:bg-slate-800 p-4 rounded-lg space-y-2">
              {worklet.students.map((student) => (
                <li key={student} className="text-gray-700 dark:text-gray-300">{student}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}