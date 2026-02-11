import { useState, useEffect } from "react";
import { ArrowLeft, UserCircle, Mail, MessageSquare, Send, X } from 'lucide-react';

export default function Suggestion({ isOpen, onClose }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    suggestionDetails: '',
  });

  // Handle a smooth fade-in and scale-up animation
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
    console.log('Suggestion Shared:', formData);
    // In a real application, you would send this data to a database or API
    // For this example, we log it and close the modal
    onClose();
  };

  // Only render the modal if isOpen is true
  if (!isOpen) return null;

  return (
    // Modal Overlay
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      {/* Modal Content with animation */}
      <div
        className={`relative w-11/12 max-w-2xl transform rounded-xl bg-white p-8 shadow-2xl transition-all duration-300 dark:bg-slate-800 ${
          isModalVisible ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
        }`}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full p-2 text-gray-400 transition-colors hover:bg-gray-200 hover:text-gray-600 dark:hover:bg-slate-700 dark:hover:text-slate-200"
        >
          <X className="h-6 w-6" />
        </button>

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-green-500">
            Share a Suggestion
          </h1>
          <p className="text-gray-600 dark:text-slate-400 mt-2">
            Send a suggestion to a mentor or teacher via email.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Recipient Name and Email */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-slate-300">Recipient's Full Name</label>
              <div className="relative mt-1 rounded-md shadow-sm">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <UserCircle className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  name="name"
                  id="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="block w-full rounded-md border border-gray-300 pl-10 pr-4 py-2 focus:border-green-500 focus:ring-green-500 dark:bg-slate-700 dark:border-slate-600 dark:text-white"
                  placeholder="John Doe"
                  required
                />
              </div>
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-slate-300">Recipient's Email Address</label>
              <div className="relative mt-1 rounded-md shadow-sm">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="email"
                  name="email"
                  id="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="block w-full rounded-md border border-gray-300 pl-10 pr-4 py-2 focus:border-green-500 focus:ring-green-500 dark:bg-slate-700 dark:border-slate-600 dark:text-white"
                  placeholder="recipient@example.com"
                  required
                />
              </div>
            </div>
          </div>

          {/* Suggestion Details */}
          <div>
            <label htmlFor="suggestionDetails" className="block text-sm font-medium text-gray-700 dark:text-slate-300">Your Suggestion</label>
            <div className="relative mt-1 rounded-md shadow-sm">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-start pt-3 pl-3">
                <MessageSquare className="h-5 w-5 text-gray-400" />
              </div>
              <textarea
                id="suggestionDetails"
                name="suggestionDetails"
                rows="6"
                value={formData.suggestionDetails}
                onChange={handleChange}
                className="block w-full rounded-md border border-gray-300 pl-10 pr-4 py-2 focus:border-green-500 focus:ring-green-500 dark:bg-slate-700 dark:border-slate-600 dark:text-white"
                placeholder="Please provide a clear and concise suggestion. For example, 'I think we could improve our class discussions by...' or 'I have an idea for a new project related to...'"
                required
              ></textarea>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-center">
            <button
              type="submit"
              className="w-full sm:w-auto px-8 py-3 text-lg font-semibold text-white bg-gradient-to-r from-blue-500 to-green-600 rounded-full shadow-lg hover:from-blue-600 hover:to-green-700 transition duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              <div className="flex items-center justify-center space-x-2">
                <Send className="w-5 h-5" />
                <span>Send Suggestion</span>
              </div>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}