import { useState, useEffect } from 'react'
import { basketball } from '../services/api'

export default function Basketball() {
  const [games, setGames] = useState([])
  const [season, setSeason] = useState(2024)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadGames()
  }, [season])

  async function loadGames() {
    setLoading(true)
    try {
      const res = await basketball.getGames(season)
      setGames(res.data.games || [])
    } catch (e) {
      setGames([])
    }
    setLoading(false)
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24 }}>
        <h2>Basketball</h2>
        <select value={season} onChange={e => setSeason(Number(e.target.value))}>
          <option value={2024}>2024-25</option>
          <option value={2023}>2023-24</option>
          <option value={2022}>2022-23</option>
        </select>
      </div>

      {loading ? (
        <p style={{ color: '#8b98a5' }}>Chargement...</p>
      ) : games.length > 0 ? (
        <div className="card">
          <h3 style={{ marginBottom: 16 }}>Matchs recents</h3>
          {games.map((game, i) => (
            <div key={i} style={{ padding: 12, borderBottom: '1px solid #2f3942', display: 'flex', justifyContent: 'space-between' }}>
              <span>{game.home_team?.full_name} vs {game.visitor_team?.full_name}</span>
              <span style={{ color: '#1d9bf0' }}>
                {game.home_team_score} - {game.visitor_team_score}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <div className="card">
          <p style={{ color: '#8b98a5' }}>
            Configurez votre cle API balldontlie.io dans <code>backend/.env</code> pour voir les donnees.
          </p>
        </div>
      )}
    </div>
  )
}
