export default function StatCard({
  value,
  label,
  icon,
  accent = "from-white to-white",
}) {
  return (
    <div
      className={`flex items-center gap-3 bg-gradient-to-b ${accent} rounded-2xl border border-gray-200 px-4 py-3 w-40 transition-all duration-300 cursor-pointer overflow-hidden hover:shadow-lg group dark:border-slate-700`}
    >
      <div className="p-2 bg-white rounded-xl border border-gray-200 shadow-sm transition-all duration-300 group-hover:scale-110 group-hover:shadow-md dark:bg-slate-700 dark:border-slate-600">
        {icon}
      </div>
      <div className="transition-all duration-300 group-hover:scale-105">
        <div className="text-xl font-bold leading-none dark:text-white">{value}</div>
        <div className="text-xs text-gray-500 dark:text-slate-400">{label}</div>
      </div>
    </div>
  );
}