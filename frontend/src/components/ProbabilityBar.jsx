export default function ProbabilityBar({ homeProb, drawProb, awayProb, homeLabel, awayLabel }) {
  const home = Math.round(homeProb * 100)
  const draw = Math.round(drawProb * 100)
  const away = Math.round(awayProb * 100)

  return (
    <div style={{ marginTop: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: '0.85rem' }}>
        <span>{homeLabel || 'Home'} ({home}%)</span>
        <span>Draw ({draw}%)</span>
        <span>{awayLabel || 'Away'} ({away}%)</span>
      </div>
      <div style={{ display: 'flex', height: 10, borderRadius: 5, overflow: 'hidden', gap: 2 }}>
        <div className="prob-home" style={{ width: `${home}%` }} />
        <div className="prob-draw" style={{ width: `${draw}%` }} />
        <div className="prob-away" style={{ width: `${away}%` }} />
      </div>
    </div>
  )
}
