import React, { useState } from "react";

export default function SuggestionModal({ isOpen, onClose }) {
  const [worklet, setWorklet] = useState("");
  const [suggestion, setSuggestion] = useState("");

  const handleSubmit = () => {
    alert("Suggestion Shared ✅");
    onClose(); // close the modal
  };

  if (!isOpen) return null; // don't show when closed

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
      {/* ++ Dark theme styles added to modal container ++ */}
      <div className="bg-white rounded-2xl shadow-xl p-6 w-[400px] relative dark:bg-slate-800">
        <button
          // ++ Dark theme styles added to close button ++
          className="absolute top-2 right-2 text-3xl text-purple-700 hover:text-purple-900 font-bold z-10 w-10 h-10 flex items-center justify-center rounded-full hover:bg-purple-100 transition-colors dark:text-purple-300 dark:hover:text-purple-200 dark:hover:bg-slate-700"
          onClick={onClose}
        >
          ×
        </button>
        {/* ++ Dark theme styles added to heading ++ */}
        <h2 className="text-lg font-semibold mb-4 text-center text-blue-700 dark:text-blue-300">
          Share Suggestion
        </h2>

        {/* Dropdown */}
        {/* ++ Dark theme styles added to label ++ */}
        <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-slate-300">
          Select Worklet ID
        </label>
        <select
          value={worklet}
          onChange={(e) => setWorklet(e.target.value)}
          // ++ Dark theme styles added to select input ++
          className="w-full p-2 border rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-400 dark:bg-slate-700 dark:text-white dark:border-slate-600 dark:focus:ring-blue-500"
        >
          <option value="">-- Select --</option>
          <option value="25TST05SRM">25TST05SRM</option>
          <option value="25TST">25TST</option>
          <option value="11BMS">11BMS</option>
          <option value="25TST04VIT">25TST04VIT</option>
        </select>

        {/* Text area */}
        <textarea
          value={suggestion}
          onChange={(e) => setSuggestion(e.target.value)}
          placeholder="Type your suggestion here..."
          // ++ Dark theme styles added to textarea ++
          className="w-full h-24 p-2 border rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-400 dark:bg-slate-700 dark:text-white dark:border-slate-600 dark:placeholder-slate-400 dark:focus:ring-blue-500"
        />

        {/* Buttons */}
        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            // ++ Dark theme styles added to cancel button ++
            className="px-4 py-2 bg-gray-300 rounded-lg hover:bg-gray-400 dark:bg-slate-600 dark:hover:bg-slate-500 dark:text-slate-200"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            // ++ Dark theme styles added to submit button ++
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600"
          >
            Share Suggestion
          </button>
        </div>
      </div>
    </div>
  );
}