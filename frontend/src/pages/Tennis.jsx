import { useState, useEffect } from 'react'
import { tennis } from '../services/api'
import ProbabilityBar from '../components/ProbabilityBar'

export default function Tennis() {
  const [players, setPlayers] = useState([])
  const [playerA, setPlayerA] = useState('')
  const [playerB, setPlayerB] = useState('')
  const [surface, setSurface] = useState('hard')
  const [prediction, setPrediction] = useState(null)

  useEffect(() => {
    tennis.getPlayers().then(res => {
      setPlayers(res.data.players || [])
    }).catch(() => {})
  }, [])

  async function handlePredict() {
    if (!playerA || !playerB || playerA === playerB) return
    try {
      const res = await tennis.predict(playerA, playerB, surface)
      setPrediction(res.data)
    } catch (e) {
      setPrediction(null)
    }
  }

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>Tennis</h2>

      <div className="card">
        <h3 style={{ marginBottom: 16 }}>Prediction de match</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16 }}>
          <div className="form-group">
            <label>Joueur A</label>
            <select value={playerA} onChange={e => setPlayerA(e.target.value)} style={{ width: '100%' }}>
              <option value="">Selectionner...</option>
              {players.map(p => (
                <option key={p.id} value={p.id}>{p.name} (ELO: {p.elo})</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Joueur B</label>
            <select value={playerB} onChange={e => setPlayerB(e.target.value)} style={{ width: '100%' }}>
              <option value="">Selectionner...</option>
              {players.map(p => (
                <option key={p.id} value={p.id}>{p.name} (ELO: {p.elo})</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Surface</label>
            <select value={surface} onChange={e => setSurface(e.target.value)} style={{ width: '100%' }}>
              <option value="hard">Dur</option>
              <option value="clay">Terre battue</option>
              <option value="grass">Gazon</option>
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
            homeLabel={prediction.player_a}
            awayLabel={prediction.player_b}
          />
          <p style={{ color: '#8b98a5', fontSize: '0.85rem', marginTop: 12 }}>
            Surface: {prediction.surface} | Modele: ELO + bonus surface
          </p>
        </div>
      )}
    </div>
  )
}
