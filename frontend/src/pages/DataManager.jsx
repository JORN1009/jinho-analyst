import { useState, useEffect } from 'react'
import axios from 'axios'
import StatCard from '../components/StatCard'

const api = axios.create({ baseURL: '/api' })

export default function DataManager() {
  const [stats, setStats] = useState(null)
  const [collecting, setCollecting] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadStats()
  }, [])

  async function loadStats() {
    try {
      const res = await api.get('/training/stats')
      setStats(res.data)
    } catch (e) {
      setStats(null)
    }
  }

  async function collectFootball() {
    setCollecting(true)
    setMessage('Collecte football lancee (peut prendre 3-5 min)...')
    try {
      await api.post('/training/collect-football?seasons=2022,2023,2024')
      setMessage('Collecte football en cours en arriere-plan!')
    } catch (e) {
      setMessage('Erreur: verifiez votre cle API football-data.org')
    }
    setCollecting(false)
    setTimeout(loadStats, 10000)
  }

  async function collectBasketball() {
    setCollecting(true)
    setMessage('Collecte basketball lancee...')
    try {
      await api.post('/training/collect-basketball?seasons=2022,2023,2024')
      setMessage('Collecte basketball en cours en arriere-plan!')
    } catch (e) {
      setMessage('Erreur: verifiez votre cle API balldontlie.io')
    }
    setCollecting(false)
    setTimeout(loadStats, 10000)
  }

  async function collectIncremental() {
    setCollecting(true)
    setMessage('Mise a jour incrementale lancee...')
    try {
      await api.post('/training/collect-incremental')
      setMessage('Mise a jour en cours!')
    } catch (e) {
      setMessage('Erreur lors de la mise a jour')
    }
    setCollecting(false)
    setTimeout(loadStats, 5000)
  }

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>Gestion des donnees</h2>

      {stats && (
        <div className="grid" style={{ marginBottom: 24 }}>
          <StatCard label="Matchs Football" value={stats.football_matches} subtitle="En base de donnees" />
          <StatCard label="Matchs Basketball" value={stats.basketball_games} subtitle="En base de donnees" />
          <StatCard
            label="Derniere collecte"
            value={stats.last_collection ? new Date(stats.last_collection).toLocaleDateString('fr-FR') : 'Jamais'}
            subtitle="Date de mise a jour"
          />
        </div>
      )}

      <div className="card">
        <h3 style={{ marginBottom: 16 }}>Collecte de donnees</h3>
        <p style={{ color: '#8b98a5', marginBottom: 16 }}>
          Recupere les resultats historiques depuis les API sportives. La premiere collecte prend quelques minutes.
        </p>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <button className="btn" onClick={collectFootball} disabled={collecting}>
            Collecter Football (2022-2024)
          </button>
          <button className="btn" onClick={collectBasketball} disabled={collecting}>
            Collecter Basketball (2022-2024)
          </button>
          <button className="btn" onClick={collectIncremental} disabled={collecting} style={{ background: '#00ba7c' }}>
            Mise a jour (aujourd'hui)
          </button>
          <button className="btn" onClick={loadStats} style={{ background: '#273340' }}>
            Rafraichir stats
          </button>
        </div>
        {message && (
          <p style={{ marginTop: 12, color: '#1d9bf0' }}>{message}</p>
        )}
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h3 style={{ marginBottom: 12 }}>Mise a jour automatique</h3>
        <p style={{ color: '#8b98a5' }}>
          Le systeme collecte automatiquement les nouveaux resultats chaque jour a 04h00.
          Les modeles sont reentraines chaque lundi a 05h00.
        </p>
      </div>
    </div>
  )
}
