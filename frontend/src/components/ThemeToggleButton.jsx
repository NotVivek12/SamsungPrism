import React, { useContext } from 'react';
import { ThemeContext } from '../context/ThemeContext'; // Import your context
import { Sun, Moon } from 'lucide-react'; // Using icons like in your dashboard

export default function ThemeToggleButton() {
  // Access the current theme and the toggle function from the context
  const { theme, toggleTheme } = useContext(ThemeContext);

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-full transition-colors duration-300
                 bg-gray-200 hover:bg-gray-300
                 dark:bg-gray-700 dark:hover:bg-gray-600"
    >
      {theme === 'light' ? (
        <Moon className="w-5 h-5 text-gray-800" />
      ) : (
        <Sun className="w-5 h-5 text-yellow-400" />
      )}
    </button>
  );
}