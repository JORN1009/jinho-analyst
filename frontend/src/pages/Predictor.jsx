import { useState } from 'react'
import { predictions } from '../services/api'
import ProbabilityBar from '../components/ProbabilityBar'

export default function Predictor() {
  const [form, setForm] = useState({
    sport: 'football',
    home_team_id: 'team_a',
    away_team_id: 'team_b',
    home_elo: 1600,
    away_elo: 1500,
    home_form: 0.7,
    away_form: 0.5,
    home_avg_goals_scored: 1.8,
    home_avg_goals_conceded: 0.9,
    away_avg_goals_scored: 1.4,
    away_avg_goals_conceded: 1.3,
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  function updateField(field, value) {
    setForm(prev => ({ ...prev, [field]: value }))
  }

  async function handleAnalyze() {
    setLoading(true)
    try {
      const res = await predictions.fullAnalysis(form)
      setResult(res.data)
    } catch (e) {
      setResult(null)
    }
    setLoading(false)
  }

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>Predictor - Analyse combinee</h2>

      <div className="card">
        <h3 style={{ marginBottom: 16 }}>Parametres du match</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <div className="form-group">
            <label>ELO Domicile</label>
            <input type="number" value={form.home_elo} onChange={e => updateField('home_elo', Number(e.target.value))} style={{ width: '100%' }} />
          </div>
          <div className="form-group">
            <label>ELO Exterieur</label>
            <input type="number" value={form.away_elo} onChange={e => updateField('away_elo', Number(e.target.value))} style={{ width: '100%' }} />
          </div>
          <div className="form-group">
            <label>Forme Domicile (0-1)</label>
            <input type="number" step="0.1" min="0" max="1" value={form.home_form} onChange={e => updateField('home_form', Number(e.target.value))} style={{ width: '100%' }} />
          </div>
          <div className="form-group">
            <label>Forme Exterieur (0-1)</label>
            <input type="number" step="0.1" min="0" max="1" value={form.away_form} onChange={e => updateField('away_form', Number(e.target.value))} style={{ width: '100%' }} />
          </div>
          <div className="form-group">
            <label>Moy. buts marques (Dom)</label>
            <input type="number" step="0.1" value={form.home_avg_goals_scored} onChange={e => updateField('home_avg_goals_scored', Number(e.target.value))} style={{ width: '100%' }} />
          </div>
          <div className="form-group">
            <label>Moy. buts encaisses (Dom)</label>
            <input type="number" step="0.1" value={form.home_avg_goals_conceded} onChange={e => updateField('home_avg_goals_conceded', Number(e.target.value))} style={{ width: '100%' }} />
          </div>
          <div className="form-group">
            <label>Moy. buts marques (Ext)</label>
            <input type="number" step="0.1" value={form.away_avg_goals_scored} onChange={e => updateField('away_avg_goals_scored', Number(e.target.value))} style={{ width: '100%' }} />
          </div>
          <div className="form-group">
            <label>Moy. buts encaisses (Ext)</label>
            <input type="number" step="0.1" value={form.away_avg_goals_conceded} onChange={e => updateField('away_avg_goals_conceded', Number(e.target.value))} style={{ width: '100%' }} />
          </div>
        </div>
        <button className="btn" onClick={handleAnalyze} disabled={loading}>
          {loading ? 'Analyse en cours...' : 'Lancer l\'analyse combinee'}
        </button>
      </div>

      {result && (
        <>
          <div className="card" style={{ marginTop: 16 }}>
            <h3 style={{ marginBottom: 16 }}>Prediction combinee</h3>
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
              <div style={{ fontSize: '1.2rem', color: '#8b98a5', marginBottom: 4 }}>Recommandation</div>
              <div style={{ fontSize: '2rem', fontWeight: 700, color: '#1d9bf0' }}>
                {result.combined_prediction.recommended.toUpperCase()}
              </div>
              <div style={{ color: '#8b98a5' }}>
                Confiance: {Math.round(result.combined_prediction.confidence * 100)}%
              </div>
            </div>
            <ProbabilityBar
              homeProb={result.combined_prediction.home_win_prob}
              drawProb={result.combined_prediction.draw_prob}
              awayProb={result.combined_prediction.away_win_prob}
              homeLabel="Domicile"
              awayLabel="Exterieur"
            />
          </div>

          <div className="grid" style={{ marginTop: 16 }}>
            <div className="card">
              <h4 style={{ color: '#f7b731', marginBottom: 12 }}>Machine Learning</h4>
              <p>Prediction: <strong>{result.models.machine_learning.prediction}</strong></p>
              <p style={{ color: '#8b98a5', fontSize: '0.85rem' }}>
                Modele: {result.models.machine_learning.model_name}
              </p>
              <ProbabilityBar
                homeProb={result.models.machine_learning.probabilities.home_win}
                drawProb={result.models.machine_learning.probabilities.draw}
                awayProb={result.models.machine_learning.probabilities.away_win}
              />
            </div>

            <div className="card">
              <h4 style={{ color: '#00ba7c', marginBottom: 12 }}>Poisson</h4>
              <p>Score attendu: <strong>{result.models.poisson.home_goals_expected} - {result.models.poisson.away_goals_expected}</strong></p>
              <p style={{ color: '#8b98a5', fontSize: '0.85rem' }}>
                Over 2.5: {Math.round(result.models.poisson.over_2_5_prob * 100)}% |
                BTTS: {Math.round(result.models.poisson.btts_prob * 100)}%
              </p>
              <ProbabilityBar
                homeProb={result.models.poisson.home_win_prob}
                drawProb={result.models.poisson.draw_prob}
                awayProb={result.models.poisson.away_win_prob}
              />
            </div>

            <div className="card">
              <h4 style={{ color: '#1d9bf0', marginBottom: 12 }}>ELO</h4>
              <p>Domicile: <strong>{result.models.elo.home_elo}</strong> | Exterieur: <strong>{result.models.elo.away_elo}</strong></p>
              <ProbabilityBar
                homeProb={result.models.elo.home_win_prob}
                drawProb={result.models.elo.draw_prob}
                awayProb={result.models.elo.away_win_prob}
              />
            </div>
          </div>
        </>
      )}
    </div>
  )
}
