import { useState, useEffect } from 'react'
import { mma } from '../services/api'
import ProbabilityBar from '../components/ProbabilityBar'

export default function MMA() {
  const [fighters, setFighters] = useState([])
  const [fighterA, setFighterA] = useState('')
  const [fighterB, setFighterB] = useState('')
  const [prediction, setPrediction] = useState(null)

  useEffect(() => {
    mma.getFighters().then(res => {
      setFighters(res.data.fighters || [])
    }).catch(() => {})
  }, [])

  async function handlePredict() {
    if (!fighterA || !fighterB || fighterA === fighterB) return
    try {
      const res = await mma.predict(fighterA, fighterB)
      setPrediction(res.data)
    } catch (e) {
      setPrediction(null)
    }
  }

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>MMA</h2>

      <div className="card">
        <h3 style={{ marginBottom: 16 }}>Prediction de combat</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <div className="form-group">
            <label>Combattant A</label>
            <select value={fighterA} onChange={e => setFighterA(e.target.value)} style={{ width: '100%' }}>
              <option value="">Selectionner...</option>
              {fighters.map(f => (
                <option key={f.id} value={f.id}>{f.name} ({f.division} - {f.style})</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Combattant B</label>
            <select value={fighterB} onChange={e => setFighterB(e.target.value)} style={{ width: '100%' }}>
              <option value="">Selectionner...</option>
              {fighters.map(f => (
                <option key={f.id} value={f.id}>{f.name} ({f.division} - {f.style})</option>
              ))}
            </select>
          </div>
        </div>
        <button className="btn" onClick={handlePredict}>Analyser</button>
      </div>

      {prediction && (
        <div className="card" style={{ marginTop: 16 }}>
          <h3 style={{ marginBottom: 12 }}>Resultat</h3>
          <div style={{ textAlign: 'center', marginBottom: 16 }}>
            <span style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1d9bf0' }}>
              {prediction.predicted_winner}
            </span>
            <span style={{ color: '#8b98a5', marginLeft: 8 }}>
              (confiance: {Math.round(prediction.confidence * 100)}%)
            </span>
          </div>
          <ProbabilityBar
            homeProb={prediction.prob_a_wins}
            drawProb={0}
            awayProb={prediction.prob_b_wins}
            homeLabel={prediction.fighter_a}
            awayLabel={prediction.fighter_b}
          />
          <p style={{ color: '#8b98a5', fontSize: '0.85rem', marginTop: 12 }}>
            Style: {prediction.style_matchup} | Avantage: {prediction.style_advantage}
          </p>
        </div>
      )}
    </div>
  )
}
