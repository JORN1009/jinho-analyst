import { useState, useEffect } from 'react'
import StatCard from '../components/StatCard'

export default function Dashboard() {
  return (
    <div>
      <h1 style={{ marginBottom: 8 }}>JINHO Analyst</h1>
      <p style={{ color: '#8b98a5', marginBottom: 32 }}>
        Plateforme d'analyse sportive multi-sport avec modeles statistiques avances
      </p>

      <div className="grid">
        <StatCard label="Sports couverts" value="4" subtitle="Football, Basketball, Tennis, MMA" />
        <StatCard label="Modeles actifs" value="3" subtitle="ELO, Poisson, Machine Learning" />
        <StatCard label="Analyse combinee" value="ML" subtitle="Random Forest + Gradient Boosting" />
      </div>

      <div className="card" style={{ marginTop: 24 }}>
        <h3 style={{ marginBottom: 16 }}>Modeles disponibles</h3>
        <div style={{ display: 'grid', gap: 16 }}>
          <div>
            <strong style={{ color: '#1d9bf0' }}>ELO Rating System</strong>
            <p style={{ color: '#8b98a5', fontSize: '0.9rem', marginTop: 4 }}>
              Systeme de classement dynamique qui s'ajuste apres chaque match.
              Inclut un bonus domicile et des ajustements par surface (tennis).
            </p>
          </div>
          <div>
            <strong style={{ color: '#00ba7c' }}>Poisson Distribution</strong>
            <p style={{ color: '#8b98a5', fontSize: '0.9rem', marginTop: 4 }}>
              Modelise la probabilite de chaque score exact en utilisant les moyennes
              de buts marques/encaisses. Calcule over/under et BTTS.
            </p>
          </div>
          <div>
            <strong style={{ color: '#f7b731' }}>Machine Learning</strong>
            <p style={{ color: '#8b98a5', fontSize: '0.9rem', marginTop: 4 }}>
              Random Forest et Gradient Boosting entraines sur 13 features:
              ELO, forme, H2H, buts moyens, jours de repos.
            </p>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h3 style={{ marginBottom: 16 }}>Guide de demarrage</h3>
        <ol style={{ color: '#8b98a5', lineHeight: 2, paddingLeft: 20 }}>
          <li>Configurez vos cles API dans <code>backend/.env</code></li>
          <li>Selectionnez un sport dans la navigation</li>
          <li>Explorez les statistiques et classements</li>
          <li>Utilisez le Predictor pour une analyse combinee</li>
        </ol>
      </div>
    </div>
  )
}
