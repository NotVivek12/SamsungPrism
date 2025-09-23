import React, { useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import prismLogo from "../assets/logo.jpeg";
export default function Login() {
    const navigate = useNavigate(); 
  const [email, setEmail] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [otpInput, setOtpInput] = useState("");
  const [otpVerified, setOtpVerified] = useState(false);
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isLogin, setIsLogin] = useState(true); // toggle login/signup
  const [role, setRole] = useState("student"); // default role

  const simulatedOtp = "123456";

  const handleLoginSubmit = (e) => {
    e.preventDefault();
    if (!email || !password) {
      setMessage("Please fill all fields.");
      return;
    }
    setMessage(`Login successful as ${role}!`);
alert(`Login successful as ${role}!`);
navigate("/home");
};

const sendOtp = (e) => {
  e.preventDefault();
  if (!email) {
    setMessage("Please enter your email.");
    return;
  }
  setOtpSent(true);
  setOtpVerified(false);
  setOtpInput("");
  setMessage(`OTP sent to ${email} (simulated: ${simulatedOtp})`);
  alert(`OTP sent to ${email} (simulated): ${simulatedOtp}`);
};


  const verifyOtp = (e) => {
    e.preventDefault();
    if (otpInput === simulatedOtp) {
      setOtpVerified(true);
      setMessage("OTP verified successfully!");
      alert("OTP verified successfully!");
    } else {
      setMessage("Invalid OTP, please try again.");
      alert("Invalid OTP, please try again.");
    }
  };

  const handleSignupSubmit = (e) => {
    e.preventDefault();
    if (!otpVerified) {
      setMessage("Please verify OTP before signing up.");
      return;
    }
    if (!password) {
      setMessage("Please enter a password.");
      return;
    }
    setMessage("Signup successful!");
    alert("Signup successful!");
  };

  const toggleMode = () => {
    setIsLogin((prev) => !prev);
    setEmail("");
    setOtpSent(false);
    setOtpVerified(false);
    setOtpInput("");
    setPassword("");
    setMessage("");
  };

  return (
   <div className="flex min-h-screen items-center justify-center bg-gray-50 px-2"
   style={{
    backgroundImage: "linear-gradient(to right, #e0e7ff, #f3e8ff, #bae6fd)",
  }}
>
      <div className="flex w-full max-w-3xl rounded-xl bg-white shadow-md overflow-hidden">
        {/* Login Card */}
        <div className="w-full md:w-1/2 p-8 flex flex-col justify-center">
          <h2 className="mb-6 text-center text-2xl font-bold text-gray-800">
            {isLogin ? "Login" : "Sign Up"}
          </h2>
          {message && (
            <p className="mb-4 text-center text-sm text-red-500">{message}</p>
          )}
        <form
          onSubmit={isLogin ? handleLoginSubmit : handleSignupSubmit}
          className="space-y-4"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Email:
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-lg border px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              required
            />
          </div>

          {!isLogin && (
            <>
              <div>
                <button
                  onClick={sendOtp}
                  className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
                >
                  {otpSent ? "Resend OTP" : "Send OTP"}
                </button>
              </div>

              {otpSent && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Enter OTP:
                  </label>
                  <input
                    type="text"
                    value={otpInput}
                    onChange={(e) => setOtpInput(e.target.value)}
                    className="mt-1 w-full rounded-lg border px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                  <button
                    onClick={verifyOtp}
                    className="mt-2 w-full rounded-lg bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700"
                  >
                    Verify OTP
                  </button>
                </div>
              )}
            </>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Password:
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Role:
            </label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="mt-1 w-full rounded-lg border px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="student">Student</option>
              <option value="mentor">Mentor</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <button
            type="submit"
            className="w-full rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700"
          >
            {isLogin ? "Login" : "Sign Up"}
          </button>
        </form>

         <p className="mt-10 text-center text-sm text-gray-600">
            {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
            <button
              onClick={toggleMode}
              className="text-indigo-600 hover:underline"
            >
              {isLogin ? "Sign up" : "Login"}
            </button>
          </p>
        </div>
        {/* Image Section */}
        <div className="hidden md:flex md:w-1/2  h screen items-center justify-center bg-indigo-50">
          <img
            src={prismLogo}
            alt="Prism Logo"
            className="h-full w-full object-cover"
          />
        </div>
      </div>
    </div>
  );
}