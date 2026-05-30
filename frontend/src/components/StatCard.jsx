export default function StatCard({ label, value, subtitle }) {
  return (
    <div className="card" style={{ textAlign: 'center' }}>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
      {subtitle && <div style={{ color: '#8b98a5', fontSize: '0.75rem', marginTop: 4 }}>{subtitle}</div>}
    </div>
  )
}
