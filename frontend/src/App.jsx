import { Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Football from './pages/Football'
import Basketball from './pages/Basketball'
import Tennis from './pages/Tennis'
import MMA from './pages/MMA'
import Predictor from './pages/Predictor'
import DataManager from './pages/DataManager'

export default function App() {
  return (
    <>
      <nav className="nav">
        <div className="nav-content">
          <div className="nav-brand">JINHO Analyst</div>
          <div className="nav-links">
            <NavLink to="/">Dashboard</NavLink>
            <NavLink to="/football">Football</NavLink>
            <NavLink to="/basketball">Basketball</NavLink>
            <NavLink to="/tennis">Tennis</NavLink>
            <NavLink to="/mma">MMA</NavLink>
            <NavLink to="/predict">Predictor</NavLink>
            <NavLink to="/data">Donnees</NavLink>
          </div>
        </div>
      </nav>
      <div className="container">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/football" element={<Football />} />
          <Route path="/basketball" element={<Basketball />} />
          <Route path="/tennis" element={<Tennis />} />
          <Route path="/mma" element={<MMA />} />
          <Route path="/predict" element={<Predictor />} />
          <Route path="/data" element={<DataManager />} />
        </Routes>
      </div>
    </>
  )
}
