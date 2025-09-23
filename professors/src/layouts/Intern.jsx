import React, { useState, useEffect } from "react";
import { Loader2, CheckCircle2, Send, Download, FileText } from "lucide-react";

// ----------------------------------------------------------------------------------
// 1. MOCK API & DATA (Unchanged)
// ----------------------------------------------------------------------------------
const workletsData = [
  {
    id: "25TST04WT",
    students: [
      { name: "Alice Johnson", email: "alice.j@university.edu", college: "State University" },
      { name: "Bob Williams", email: "bob.w@university.edu", college: "State University" },
    ],
  },
  {
    id: "25TST05SRM",
    students: [
      { name: "Diana Prince", email: "diana.p@metro.edu", college: "Metropolis University" },
      { name: "Clark Kent", email: "clark.k@metro.edu", college: "Metropolis University" },
    ],
  },
];
const currentMentor = { mentorName: "Mary Christian", mentorEmail: "mary.c@samsung.com" };

const fetchStudentsForWorklet = (workletId) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const worklet = workletsData.find((w) => w.id === workletId);
      resolve(worklet ? worklet.students : []);
    }, 700);
  });
};

// ----------------------------------------------------------------------------------
// 2. CUSTOM HOOK (Unchanged)
// ----------------------------------------------------------------------------------
const useWorkletStudents = (workletId) => {
  const [students, setStudents] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  useEffect(() => {
    if (!workletId) {
      setStudents([]);
      return;
    }
    const getStudents = async () => {
      setIsLoading(true);
      const fetchedStudents = await fetchStudentsForWorklet(workletId);
      setStudents(fetchedStudents);
      setIsLoading(false);
    };
    getStudents();
  }, [workletId]);
  return { students, isLoading };
};

// ----------------------------------------------------------------------------------
// 3. MAIN UI COMPONENT (Updated with Dark Theme)
// ----------------------------------------------------------------------------------
const initialFormData = {
  workletId: "",
  studentName: "",
  studentEmail: "",
  studentCollege: "",
  referralCriteria: [],
  reason: "",
};

export default function InternReferralForm() {
  const [formData, setFormData] = useState(initialFormData);
  const [status, setStatus] = useState("idle");
  const [submittedData, setSubmittedData] = useState(null);
  const { students, isLoading: areStudentsLoading } = useWorkletStudents(
    formData.workletId
  );

  useEffect(() => {
    if (formData.studentName && students.length > 0) {
      const student = students.find((s) => s.name === formData.studentName);
      setFormData((prev) => ({
        ...prev,
        studentEmail: student?.email || "",
        studentCollege: student?.college || "",
      }));
    }
  }, [formData.studentName, students]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => {
      const newState = { ...prev, [name]: value };
      if (name === "workletId") {
        newState.studentName = "";
        newState.studentEmail = "";
        newState.studentCollege = "";
      }
      return newState;
    });
  };

  const handleCheckboxChange = (value) => {
    setFormData((prev) => ({
      ...prev,
      referralCriteria: prev.referralCriteria.includes(value)
        ? prev.referralCriteria.filter((c) => c !== value)
        : [...prev.referralCriteria, value],
    }));
  };

  const handleReset = () => {
    setFormData(initialFormData);
    setSubmittedData(null);
    setStatus("idle");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus("submitting");
    const finalData = { ...formData, ...currentMentor };
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setSubmittedData(finalData);
    setStatus("success");
  };
  
  const criteriaOptions = [
    { value: "exemplary", label: "Exemplary Performance: Consistently exceeds expectations." },
    { value: "teamwork", label: "Teamwork: Works collaboratively and contributes to team success." },
    { value: "leadership", label: "Leadership: Demonstrates leadership and initiative." },
    { value: "innovation", label: "Innovation: Suggests new ideas or methods that help improve the worklet." },
    { value: "problemSolving", label: "Problem-Solving Ability: Approaches challenges with logical thinking." },
    { value: "positiveAttitude", label: "Positive Attitude: Maintains a positive attitude and morale within the team." },
    { value: "communication", label: "Communication: Expresses ideas and concerns clearly." },
    { value: "learningAgility", label: "Learning Agility: Picks up new skills or tools quickly and applies feedback to improve." }
  ];

  if (status === "success") {
    return <SuccessScreen submittedData={submittedData} onReset={handleReset} />;
  }
  
  return (
    // ++ Dark theme styles added
    <div className="flex justify-center items-center min-h-screen bg-blue-50 dark:bg-slate-900 p-6">
      <form
        onSubmit={handleSubmit}
        // ++ Dark theme styles added
        className="bg-white shadow-lg border-2 border-blue-300 rounded-xl p-8 w-full max-w-3xl dark:bg-slate-800 dark:border-slate-700"
      >
        {/* ++ Dark theme styles added */}
        <h1 className="text-center text-2xl font-extrabold text-blue-700 dark:text-blue-300 mb-4">
          INTERN REFERRAL FORM
        </h1>
        {/* ++ Dark theme styles added */}
        <p className="text-sm text-gray-600 dark:text-slate-400 text-center mb-6">
          This form allows you to refer a PRISM mentee for our internship process.
          Your referral will be reviewed by our team and we'll reach out if the profile aligns with our criteria.
        </p>

        {/* Mentor Info Section */}
        <h2 className="font-bold text-blue-600 dark:text-blue-400 mb-2">Mentor Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* ++ Dark theme styles added */}
          <input type="text" value={currentMentor.mentorName} readOnly className="border rounded-md p-2 w-full bg-gray-100 dark:bg-slate-700 dark:text-slate-300 dark:border-slate-600" />
          <input type="email" value={currentMentor.mentorEmail} readOnly className="border rounded-md p-2 w-full bg-gray-100 dark:bg-slate-700 dark:text-slate-300 dark:border-slate-600" />
        </div>

        {/* Student Info Section */}
        <h2 className="font-bold text-blue-600 dark:text-blue-400 mb-2">PRISM Mentee Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* ++ Dark theme styles added */}
          <select name="workletId" value={formData.workletId} onChange={handleChange} required className="border rounded-md p-2 w-full dark:bg-slate-700 dark:text-white dark:border-slate-600">
            <option value="" disabled>Select a Worklet ID</option>
            {workletsData.map((w) => (<option key={w.id} value={w.id}>{w.id}</option>))}
          </select>

          {/* ++ Dark theme styles added */}
          <select name="studentName" value={formData.studentName} onChange={handleChange} disabled={!formData.workletId || areStudentsLoading} required className="border rounded-md p-2 w-full dark:bg-slate-700 dark:text-white dark:border-slate-600">
            <option value="" disabled>
              {!formData.workletId ? "First, select a worklet" : areStudentsLoading ? "Loading students..." : "Select a Student"}
            </option>
            {students.map((s) => (<option key={s.name} value={s.name}>{s.name}</option>))}
          </select>

          {/* ++ Dark theme styles added */}
          <input type="email" value={formData.studentEmail} placeholder="Student Email (auto-filled)" readOnly className="border rounded-md p-2 w-full bg-gray-100 dark:bg-slate-700 dark:text-slate-300 dark:border-slate-600" />
          <input type="text" value={formData.studentCollege} placeholder="Student College (auto-filled)" readOnly className="border rounded-md p-2 w-full bg-gray-100 dark:bg-slate-700 dark:text-slate-300 dark:border-slate-600" />
        </div>

        {/* Referral Criteria Section */}
        <h2 className="font-bold text-blue-600 dark:text-blue-400 mb-2">Referral Criteria</h2>
        <div className="flex flex-col gap-2 mb-6">
          {criteriaOptions.map((criteria) => (
            <label key={criteria.value} className="flex items-start space-x-2 cursor-pointer">
              <input type="checkbox" checked={formData.referralCriteria.includes(criteria.value)} onChange={() => handleCheckboxChange(criteria.value)} className="mt-1 h-4 w-4" />
              {/* ++ Dark theme styles added */}
              <span className="text-sm text-gray-700 dark:text-slate-300">{criteria.label}</span>
            </label>
          ))}
        </div>

        {/* Reason for Referring Section */}
        <h2 className="font-bold text-blue-600 dark:text-blue-400 mb-2">Reason for Referring</h2>
        {/* ++ Dark theme styles added */}
        <textarea name="reason" value={formData.reason} onChange={handleChange} placeholder="Please provide a detailed explanation..." className="border rounded-md p-3 w-full h-28 mb-6 dark:bg-slate-700 dark:text-white dark:border-slate-600 dark:placeholder-slate-400" required />

        {/* Submit Button */}
        <div className="text-center">
          {/* ++ Dark theme styles added */}
          <button type="submit" disabled={status === "submitting"} className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-full font-semibold shadow-md flex items-center justify-center gap-2 mx-auto disabled:bg-blue-400 disabled:cursor-not-allowed dark:bg-blue-500 dark:hover:bg-blue-600 dark:disabled:bg-blue-500/50">
            {status === "submitting" ? (<Loader2 className="animate-spin w-5 h-5" />) : (<Send className="w-5 h-5" />)}
            {status === "submitting" ? "Submitting..." : "Submit Referral"}
          </button>
        </div>
      </form>
    </div>
  );
}

// ----------------------------------------------------------------------------------
// 4. SUCCESS SCREEN (Updated with Dark Theme)
// ----------------------------------------------------------------------------------
function SuccessScreen({ submittedData, onReset }) {
  const handleDownload = () => {
    // ... handleDownload function remains unchanged
  };

  return (
    // ++ Dark theme styles added
    <div className="flex justify-center items-center min-h-screen bg-blue-50 dark:bg-slate-900 p-6">
      {/* ++ Dark theme styles added */}
      <div className="text-center p-10 bg-white rounded-xl shadow-lg border-2 border-blue-300 max-w-3xl mx-auto dark:bg-slate-800 dark:border-slate-700">
        <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
        {/* ++ Dark theme styles added */}
        <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-2">Referral Submitted!</h2>
        <p className="text-gray-600 dark:text-slate-400 mb-8">
          Thank you for your feedback. You can download a copy for your records.
        </p>
        <div className="flex justify-center items-center gap-4">
          {/* ++ Dark theme styles added */}
          <button onClick={handleDownload} className="bg-gray-700 text-white font-semibold px-6 py-2 rounded-lg hover:bg-gray-800 flex items-center gap-2 dark:bg-slate-600 dark:hover:bg-slate-500">
            <Download className="w-5 h-5" /> Download
          </button>
          {/* ++ Dark theme styles added */}
          <button onClick={onReset} className="bg-blue-600 text-white font-semibold px-6 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2 dark:bg-blue-500 dark:hover:bg-blue-600">
            <FileText className="w-5 h-5" /> Submit Another
          </button>
        </div>
      </div>
    </div>
  );
}