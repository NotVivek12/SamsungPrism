import { useState, useEffect } from "react";
import { ArrowLeft, UserCircle, Mail, Info, Paperclip, X } from 'lucide-react';

export default function RequestUpdate({ isOpen, onClose }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    updateType: '',
    updateDetails: '',
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
    console.log('Update Request Submitted:', formData);
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
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-500 to-indigo-500">
            Request Profile Update
          </h1>
          <p className="text-gray-600 dark:text-slate-400 mt-2">
            Use this form to request changes to your professor profile.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Name and Email */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-slate-300">Full Name</label>
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
                  className="block w-full rounded-md border border-gray-300 pl-10 pr-4 py-2 focus:border-indigo-500 focus:ring-indigo-500 dark:bg-slate-700 dark:border-slate-600 dark:text-white"
                  placeholder="Jane Doe"
                  required
                />
              </div>
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-slate-300">Email Address</label>
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
                  className="block w-full rounded-md border border-gray-300 pl-10 pr-4 py-2 focus:border-indigo-500 focus:ring-indigo-500 dark:bg-slate-700 dark:border-slate-600 dark:text-white"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>
          </div>

          {/* Update Type */}
          <div>
            <label htmlFor="updateType" className="block text-sm font-medium text-gray-700 dark:text-slate-300">Type of Information to Update</label>
            <div className="relative mt-1 rounded-md shadow-sm">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <Info className="h-5 w-5 text-gray-400" />
              </div>
              <select
                id="updateType"
                name="updateType"
                value={formData.updateType}
                onChange={handleChange}
                className="block w-full rounded-md border border-gray-300 pl-10 pr-4 py-2 focus:border-indigo-500 focus:ring-indigo-500 dark:bg-slate-700 dark:border-slate-600 dark:text-white"
                required
              >
                <option value="">-- Please select an option --</option>
                <option value="bio">Biography</option>
                <option value="education">Education</option>
                <option value="experience">Experience</option>
                <option value="researchPapers">Research Papers</option>
                <option value="projects">Key Projects</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>

          {/* Update Details */}
          <div>
            <label htmlFor="updateDetails" className="block text-sm font-medium text-gray-700 dark:text-slate-300">Details of your request</label>
            <div className="relative mt-1 rounded-md shadow-sm">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-start pt-3 pl-3">
                <Paperclip className="h-5 w-5 text-gray-400" />
              </div>
              <textarea
                id="updateDetails"
                name="updateDetails"
                rows="6"
                value={formData.updateDetails}
                onChange={handleChange}
                className="block w-full rounded-md border border-gray-300 pl-10 pr-4 py-2 focus:border-indigo-500 focus:ring-indigo-500 dark:bg-slate-700 dark:border-slate-600 dark:text-white"
                placeholder="Please provide clear and concise details about the information you want to update. Include links to research papers or project websites if applicable."
                required
              ></textarea>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-center">
            <button
              type="submit"
              className="w-full sm:w-auto px-8 py-3 text-lg font-semibold text-white bg-gradient-to-r from-blue-500 to-purple-600 rounded-full shadow-lg hover:from-blue-600 hover:to-purple-700 transition duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Submit Request
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
