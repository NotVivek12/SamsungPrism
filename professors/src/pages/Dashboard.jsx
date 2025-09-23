import React, { useState, useEffect } from "react";
import prismlogo from '../assets/prism_logo.png';
import RequestUpdate from "../layouts/RequestUpdate";
import ScheduleMeeting from "../layouts/ScheduleMeeting";
import Feedback from "../layouts/FeedBack";
import ComprehensiveTeacherSearch from "../components/ComprehensiveTeacherSearch";

import {
  Home, BarChart, GraduationCap, MessageSquare, Bell, Calendar,
  MessageCircle, Zap, Rocket, Key, Crown, PlusCircle, Bot, UserCircle, Columns, Lightbulb
} from "lucide-react";

// The entire application is contained within this single file,
// including all components, styles, and logic.

// Reusable components defined locally
const SidebarItem = ({ icon, label, onClick }) => (
  <button onClick={onClick} className="flex flex-col items-center justify-center p-3 rounded-xl hover:bg-white/10 transition-colors duration-200 group">
    {icon}
    <span className="text-xs text-center mt-1 text-slate-900 font-medium group-hover:text-slate-900 dark:text-slate-300 dark:group-hover:text-white">{label}</span>
  </button>
);

const ActivityButton = ({ icon, label, onClick }) => (
  <button onClick={onClick} className="w-full flex items-center gap-4 py-3 px-4 rounded-xl hover:bg-slate-200 transition-colors duration-200 mb-2 dark:hover:bg-slate-700">
    {icon}
    {label}
  </button>
);

const ThemeToggleButton = () => {
  const [isDark, setIsDark] = useState(false);
  const toggleTheme = () => {
    setIsDark(!isDark);
    document.documentElement.classList.toggle('dark');
  };
  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-white transition-colors duration-200"
    >
      {isDark ? (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      ) : (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0015.354 20.354z" />
        </svg>
      )}
    </button>
  );
};

// Simple Modal component
const Modal = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50 p-4 overflow-y-auto">
      <div className="relative w-full max-w-3xl bg-white rounded-xl mt-10 mb-10 dark:bg-slate-800">
        <div className="sticky top-0 right-0 flex justify-end bg-white rounded-t-xl p-2 dark:bg-slate-800">
          <button
            onClick={onClose}
            className="text-3xl text-purple-700 hover:text-purple-900 font-bold z-10 w-10 h-10 flex items-center justify-center rounded-full hover:bg-purple-100 transition-colors dark:text-purple-400 dark:hover:bg-purple-900"
          >
            ×
          </button>
        </div>
        <div className="p-6">
          {children}
        </div>
      </div>
    </div>
  );
};


// Main App component
export default function App() {
  const [isRequestUpdateOpen, setIsRequestUpdateOpen] = useState(false);
  const [isScheduleOpen, setIsScheduleOpen] = useState(false);
  const [isSuggestionModalOpen, setIsSuggestionModalOpen] = useState(false);
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);

  const handleNavigation = (path) => {
    console.log(`Simulating navigation to: ${path}`);
    // In a real application with react-router-dom, this would be:
    // navigate(path);
  };

  return (
    <div className="flex h-screen w-full bg-slate-50 text-gray-800 overflow-hidden dark:bg-slate-900 dark:text-slate-200">
      {/* Left Sidebar */}
      <aside className="w-20 lg:w-30 bg-gradient-to-t from-purple-300 via-indigo-50 to-blue-100 dark:from-slate-800 dark:via-slate-900 dark:to-black flex flex-col py-2 overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
        <nav className="flex flex-col gap-6 items-center">
          <SidebarItem icon={<Home className="w-5 h-5" />} label="Home" onClick={() => handleNavigation("/home")} />
          <SidebarItem icon={<BarChart className="w-5 h-5" />} label="Knowledge Graph" onClick={() => handleNavigation("/statistics")} />
          <SidebarItem icon={<GraduationCap className="w-5 h-5" />} label="Colleges" onClick={() => handleNavigation("/colleges")} />
          <SidebarItem icon={<MessageSquare className="w-5 h-5" />} label="Chats" onClick={() => handleNavigation("/chats")} />
          <SidebarItem icon={<Bell className="w-5 h-5" />} label="Updates" onClick={() => handleNavigation("/updates")} />
          <SidebarItem icon={<MessageCircle className="w-5 h-5" />} label="Feedbacks" onClick={() => setIsFeedbackOpen(true)} />
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 px-8 py-6 overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-4xl font-bold mb-4 text-blue-900 dark:text-white">
              Faculty Research Directory
            </h1>
            <p className="text-sm text-gray-500 dark:text-slate-400">
              PRISM / Research Discovery Platform
            </p>
          </div>
          <div className="flex items-center gap-4">
            <ThemeToggleButton />
            <img
              src={prismlogo}
              alt="PRISM"
              className="h-20 opacity-90"
            />
          </div>
        </div>
        
        {/* Comprehensive Teacher Search Component */}
        <ComprehensiveTeacherSearch />
      </main>
      
      {/* Right Sidebar */}
      <aside className="w-64 bg-gradient-to-t from-purple-300 via-indigo-50 to-blue-100 dark:from-slate-800 dark:via-slate-900 dark:to-black shadow-lg px-4 py-6 flex flex-col justify-between overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
        <div>
          <button
            className="w-full bg-blue-100 hover:bg-blue-200 text-blue-900 font-bold rounded-xl py-2 mb-4 flex items-center justify-center gap-2 text-xl dark:bg-blue-900/50 dark:hover:bg-blue-800/60 dark:text-blue-200"
            onClick={() => handleNavigation("/new-worklet")}
          >
            <PlusCircle className="w-5 h-10" /> <span className="text-2xl">New Professor</span>
          </button>
          <h2 className="text-2xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-cyan-500">Activities</h2>
          <ActivityButton
            icon={<Zap className="w-5 h-10 text-blue-600" />}
            label={<span className="text-lg font-semibold">Request Update</span>}
            onClick={() => setIsRequestUpdateOpen(true)}
          />
          <ActivityButton
            icon={<Lightbulb className="w-5 h-10 text-sky-500" />}
            label={<span className="text-lg font-semibold">Share Suggestion</span>}
            onClick={() => setIsSuggestionModalOpen(true)}
          />
          <ActivityButton
            icon={<Calendar className="w-5 h-10 text-blue-600" />}
            label={<span className="text-lg font-semibold">Schedule Meeting</span>}
            onClick={() => setIsScheduleOpen(true)}
          />
        
          <ActivityButton
            icon={<MessageSquare className="w-5 h-10 text-indigo-600" />}
            label={<span className="text-lg font-semibold">Submit Feedback</span>}
            onClick={() => setIsFeedbackOpen(true)}
          />
        </div>
        <div className="text-center">
          <button
            onClick={() => handleNavigation("/ray")}
            className="group relative mx-auto w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-400 to-blue-400 
                      hover:from-purple-500 hover:to-blue-500 flex items-center justify-center 
                      text-lg font-bold text-white shadow transition-all duration-200 
                      hover:shadow-lg transform hover:scale-105 cursor-pointer overflow-hidden"
            aria-label="RAY Support Bot"
          >
            <span className="absolute transition-opacity duration-200 opacity-100 group-hover:opacity-0">
              <Bot className="w-8 h-8" />
            </span>
            <span className="absolute transition-opacity duration-500 opacity-0 group-hover:opacity-100">
              RAY
            </span>
          </button>
          <p className="text-sm text-gray-600 mt-1 dark:text-slate-400">Support</p>
        </div>
      </aside>

      {/* Modals defined inline */}
      <RequestUpdate
        isOpen={isRequestUpdateOpen}
        onClose={() => setIsRequestUpdateOpen(false)}
      />

      <Modal
        isOpen={isSuggestionModalOpen}
        onClose={() => setIsSuggestionModalOpen(false)}
      >
        <h2 className="text-2xl font-bold mb-4">Share Suggestion</h2>
        <p>This is a placeholder for the Share Suggestion modal content.</p>
      </Modal>

      <ScheduleMeeting
        isOpen={isScheduleOpen}
        onClose={() => setIsScheduleOpen(false)}
      />

      
      {isFeedbackOpen && (
        <Feedback onClose={() => setIsFeedbackOpen(false)} />
      )}

    </div>
  );
}
