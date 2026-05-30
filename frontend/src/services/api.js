import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

export const football = {
  getLeagues: () => api.get('/football/leagues'),
  getMatches: (league) => api.get(`/football/matches?league=${league}`),
  getStandings: (league) => api.get(`/football/standings?league=${league}`),
  getTeamForm: (teamId) => api.get(`/football/team/${teamId}/form`),
}

export const basketball = {
  getGames: (season) => api.get(`/basketball/games?season=${season}`),
  getTeamStats: (teamId, season) => api.get(`/basketball/team/${teamId}/stats?season=${season}`),
}

export const tennis = {
  getPlayers: () => api.get('/tennis/players'),
  predict: (playerA, playerB, surface) =>
    api.post(`/tennis/predict?player_a_id=${playerA}&player_b_id=${playerB}&surface=${surface}`),
}

export const mma = {
  getFighters: () => api.get('/mma/fighters'),
  predict: (fighterA, fighterB) =>
    api.post(`/mma/predict?fighter_a_id=${fighterA}&fighter_b_id=${fighterB}`),
}

export const predictions = {
  fullAnalysis: (data) => api.post('/predictions/full-analysis', data),
}

export default api
