export default function SidebarItem({ icon, label, onClick }) {
  return (
    <div 
      className="flex flex-col items-center px-4 rounded-2xl cursor-pointer 
                 text-gray-600 transition-all duration-200 transform 
                 hover:scale-105 hover:shadow-md hover:bg-white hover:text-purple-700
                 dark:text-slate-300 dark:hover:bg-slate-700 dark:hover:text-purple-400"
      onClick={onClick}
    >
      <div className="p-2">{icon}</div>
      <span className="text-sm font-semibold mt-1 text-center">{label}</span>
    </div>
  );
}