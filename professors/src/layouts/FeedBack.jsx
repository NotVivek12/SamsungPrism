import React, { useState } from "react";

const FeedBack = ({ onClose }) => {
  // Use a string for the mentor's name
  const [mentorName, setMentorName] = useState("Jane Doe");
  const [professor, setProfessor] = useState({
    id: "PROF001",
    name: "Professor Smith",
    email: "smith@university.edu",
  });
  const [feedback, setFeedback] = useState("");
  const [feedbackType, setFeedbackType] = useState("");

  const professors = [
    {
      id: "PROF001",
      name: "Professor Smith",
      email: "smith@university.edu",
    },
    {
      id: "PROF002",
      name: "Dr. Jane Doe",
      email: "j.doe@university.edu",
    },
    {
      id: "PROF003",
      name: "Mr. John Lee",
      email: "j.lee@university.edu",
    },
  ];

  const handleProfessorChange = (e) => {
    const selectedProfessorId = e.target.value;
    const selectedProfessor = professors.find(
      (p) => p.id === selectedProfessorId
    );
    setProfessor(selectedProfessor);
  };

  const handleSubmit = () => {
    const data = {
      mentorName,
      professorId: professor.id,
      professorName: professor.name,
      professorEmail: professor.email,
      feedback,
      feedbackType,
    };
    console.log("Feedback Submitted:", data);
    onClose();
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
      <div className="bg-white rounded-2xl shadow-lg w-[400px] p-5 relative dark:bg-slate-800">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-3xl text-purple-700 hover:text-purple-900 font-bold z-10 w-10 h-10 flex items-center justify-center rounded-full hover:bg-purple-100 transition-colors dark:text-purple-300 dark:hover:text-purple-200 dark:hover:bg-slate-700"
        >
          ×
        </button>
        <h2 className="text-lg font-semibold mb-4 text-center dark:text-white">
          Give Professor Feedback
        </h2>

        {/* Mentor Name (Read-only) */}
        <div className="mb-3">
          <label className="text-sm font-medium dark:text-slate-300">
            Mentor Name
          </label>
          <input
            type="text"
            value={mentorName}
            readOnly
            className="w-full border rounded-lg px-3 py-2 mt-1 bg-gray-100 dark:bg-slate-700 dark:text-gray-400 dark:border-slate-600 cursor-not-allowed"
          />
        </div>

        {/* Professor Details */}
        <div className="mb-3">
          <label className="text-sm font-medium dark:text-slate-300">
            Select Professor
          </label>
          <select
            value={professor.id}
            onChange={handleProfessorChange}
            className="w-full border rounded-lg px-3 py-2 mt-1 focus:outline-none focus:ring-2 focus:ring-blue-400 dark:bg-slate-700 dark:text-white dark:border-slate-600 dark:focus:ring-blue-500"
          >
            {professors.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>

        {/* Display Professor Info */}
        <div className="mb-3 p-3 border rounded-lg dark:border-slate-600 dark:bg-slate-700">
          <p className="text-sm dark:text-slate-300">
            <span className="font-bold">ID:</span> {professor.id}
          </p>
          <p className="text-sm dark:text-slate-300">
            <span className="font-bold">Email:</span> {professor.email}
          </p>
        </div>

        {/* Feedback */}
        <div className="mb-3">
          <textarea
            placeholder="Type your feedback for the professor here..."
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 h-24 resize-none focus:outline-none focus:ring-2 focus:ring-blue-400 dark:bg-slate-700 dark:text-white dark:border-slate-600 dark:placeholder-slate-400 dark:focus:ring-blue-500"
          />
        </div>

        {/* Feedback Type */}
        <div className="flex items-center gap-4 mb-4 dark:text-slate-300">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="feedback"
              value="general"
              checked={feedbackType === "general"}
              onChange={() => setFeedbackType("general")}
            />
            <span>General Feedback</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="feedback"
              value="course_specific"
              checked={feedbackType === "course_specific"}
              onChange={() => setFeedbackType("course_specific")}
            />
            <span>Course-Specific Feedback</span>
          </label>
        </div>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          className="w-full bg-blue-700 text-white rounded-lg py-2 hover:bg-blue-800 transition dark:bg-blue-600 dark:hover:bg-blue-700"
        >
          Send Feedback
        </button>
      </div>
    </div>
  );
};

export default FeedBack;