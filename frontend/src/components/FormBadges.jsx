export default function FormBadges({ form }) {
  if (!form || !form.length) return null

  return (
    <div style={{ display: 'flex', gap: 4 }}>
      {form.map((result, i) => (
        <span
          key={i}
          className={`badge badge-${result === 'W' ? 'win' : result === 'D' ? 'draw' : 'loss'}`}
        >
          {result}
        </span>
      ))}
    </div>
  )
}
