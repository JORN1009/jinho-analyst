import { useState, useEffect } from 'react'
import { football } from '../services/api'
import StatCard from '../components/StatCard'

export default function Football() {
  const [league, setLeague] = useState('PL')
  const [standings, setStandings] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadStandings()
  }, [league])

  async function loadStandings() {
    setLoading(true)
    try {
      const res = await football.getStandings(league)
      setStandings(res.data.standings || [])
    } catch (e) {
      setStandings([])
    }
    setLoading(false)
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24 }}>
        <h2>Football</h2>
        <select value={league} onChange={e => setLeague(e.target.value)}>
          <option value="PL">Premier League</option>
          <option value="PD">La Liga</option>
          <option value="BL1">Bundesliga</option>
          <option value="SA">Serie A</option>
          <option value="FL1">Ligue 1</option>
          <option value="CL">Champions League</option>
        </select>
      </div>

      {loading ? (
        <p style={{ color: '#8b98a5' }}>Chargement...</p>
      ) : standings.length > 0 ? (
        <div className="card">
          <h3 style={{ marginBottom: 16 }}>Classement</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ color: '#8b98a5', fontSize: '0.8rem', textAlign: 'left' }}>
                <th style={{ padding: 8 }}>#</th>
                <th style={{ padding: 8 }}>Equipe</th>
                <th style={{ padding: 8 }}>MJ</th>
                <th style={{ padding: 8 }}>V</th>
                <th style={{ padding: 8 }}>N</th>
                <th style={{ padding: 8 }}>D</th>
                <th style={{ padding: 8 }}>BP</th>
                <th style={{ padding: 8 }}>BC</th>
                <th style={{ padding: 8 }}>Pts</th>
              </tr>
            </thead>
            <tbody>
              {standings.map((team, i) => (
                <tr key={i} style={{ borderTop: '1px solid #2f3942' }}>
                  <td style={{ padding: 8 }}>{team.position}</td>
                  <td style={{ padding: 8 }}>{team.team?.name}</td>
                  <td style={{ padding: 8 }}>{team.playedGames}</td>
                  <td style={{ padding: 8 }}>{team.won}</td>
                  <td style={{ padding: 8 }}>{team.draw}</td>
                  <td style={{ padding: 8 }}>{team.lost}</td>
                  <td style={{ padding: 8 }}>{team.goalsFor}</td>
                  <td style={{ padding: 8 }}>{team.goalsAgainst}</td>
                  <td style={{ padding: 8, fontWeight: 700, color: '#1d9bf0' }}>{team.points}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="card">
          <p style={{ color: '#8b98a5' }}>
            Configurez votre cle API football-data.org dans <code>backend/.env</code> pour voir les donnees.
          </p>
        </div>
      )}
    </div>
  )
}
