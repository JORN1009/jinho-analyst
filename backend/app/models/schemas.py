from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Team(BaseModel):
    id: str
    name: str
    sport: str
    league: Optional[str] = None
    country: Optional[str] = None


class Match(BaseModel):
    id: str
    sport: str
    league: str
    home_team: Team
    away_team: Team
    date: datetime
    status: str = "scheduled"
    home_score: Optional[int] = None
    away_score: Optional[int] = None


class EloRating(BaseModel):
    team: Team
    rating: float
    last_updated: datetime


class PoissonPrediction(BaseModel):
    match_id: str
    home_goals_expected: float
    away_goals_expected: float
    home_win_prob: float
    draw_prob: float
    away_win_prob: float


class MLPrediction(BaseModel):
    match_id: str
    sport: str
    prediction: str
    confidence: float
    features_used: list[str]
    model_name: str


class PerformanceStats(BaseModel):
    team: Team
    matches_played: int
    wins: int
    draws: int
    losses: int
    form_last_5: list[str]
    avg_goals_scored: float
    avg_goals_conceded: float
    elo_rating: float
