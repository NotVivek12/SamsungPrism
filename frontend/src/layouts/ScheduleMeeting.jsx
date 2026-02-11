import { useState, useEffect } from "react";
import { UserCircle, Mail, Calendar, Clock, X } from 'lucide-react';

export default function ScheduleMeeting({ isOpen, onClose }) {
  const [formData, setFormData] = useState({
    mentorName: '',
    teacherEmail: '',
    meetingDate: '',
    meetingTime: '',
  });

  const [isModalVisible, setIsModalVisible] = useState(false);
  useEffect(() => {
    if (isOpen) {
      setIsModalVisible(true);
    } else {
      setIsModalVisible(false);
    }
  }, [isOpen]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({ ...prevState, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Meeting Scheduled:', formData);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div
        className={`relative w-11/12 max-w-2xl transform rounded-xl bg-white p-8 shadow-2xl transition-all duration-300 dark:bg-slate-800 ${
          isModalVisible ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
        }`}
      >
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full p-2 text-gray-400 transition-colors hover:bg-gray-200 hover:text-gray-600 dark:hover:bg-slate-700 dark:hover:text-slate-200"
        >
          <X className="h-6 w-6" />
        </button>

        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-500 to-indigo-500">
            Schedule a Meeting
          </h1>
          <p className="text-gray-600 dark:text-slate-400 mt-2">
            Fill out the form to request a meeting with a teacher.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="mentorName" className="block text-sm font-medium text-gray-700 dark:text-slate-300">Mentor's Name</label>
              <div className="relative mt-1 rounded-md shadow-sm">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <UserCircle className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  name="mentorName"
                  id="mentorName"
                  value={formData.mentorName}
                  onChange={handleChange}
                  className="block w-full rounded-md border border-gray-300 pl-10 pr-4 py-2 focus:border-indigo-500 focus:ring-indigo-500 dark:bg-slate-700 dark:border-slate-600 dark:text-white"
                  placeholder="John Smith"
                  required
                />
              </div>
            </div>
            <div>
              <label htmlFor="teacherEmail" className="block text-sm font-medium text-gray-700 dark:text-slate-300">Teacher's Email</label>
              <div className="relative mt-1 rounded-md shadow-sm">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="email"
                  name="teacherEmail"
                  id="teacherEmail"
                  value={formData.teacherEmail}
                  onChange={handleChange}
                  className="block w-full rounded-md border border-gray-300 pl-10 pr-4 py-2 focus:border-indigo-500 focus:ring-indigo-500 dark:bg-slate-700 dark:border-slate-600 dark:text-white"
                  placeholder="teacher@example.com"
                  required
                />
              </div>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="meetingDate" className="block text-sm font-medium text-gray-700 dark:text-slate-300">Date</label>
              <div className="relative mt-1 rounded-md shadow-sm">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <Calendar className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="date"
                  name="meetingDate"
                  id="meetingDate"
                  value={formData.meetingDate}
                  onChange={handleChange}
                  className="block w-full rounded-md border border-gray-300 pl-10 pr-4 py-2 focus:border-indigo-500 focus:ring-indigo-500 dark:bg-slate-700 dark:border-slate-600 dark:text-white"
                  required
                />
              </div>
            </div>
            <div>
              <label htmlFor="meetingTime" className="block text-sm font-medium text-gray-700 dark:text-slate-300">Time</label>
              <div className="relative mt-1 rounded-md shadow-sm">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <Clock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="time"
                  name="meetingTime"
                  id="meetingTime"
                  value={formData.meetingTime}
                  onChange={handleChange}
                  className="block w-full rounded-md border border-gray-300 pl-10 pr-4 py-2 focus:border-indigo-500 focus:ring-indigo-500 dark:bg-slate-700 dark:border-slate-600 dark:text-white"
                  required
                />
              </div>
            </div>
          </div>
          <div className="flex justify-center">
            <button
              type="submit"
              className="w-full sm:w-auto px-8 py-3 text-lg font-semibold text-white bg-gradient-to-r from-blue-500 to-purple-600 rounded-full shadow-lg hover:from-blue-600 hover:to-purple-700 transition duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Schedule Meeting
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
