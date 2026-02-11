export default function LevelBadge({ icon, label, value, color }) {
  return (
    <div
      className={`flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs font-medium ${color}`}
    >
      {icon}
      <span>{label}</span>
      <span className="ml-auto font-semibold">{value}</span>
    </div>
  );
}
