from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.ml.trainer import football_trainer
from app.services.poisson_service import poisson_service
from app.services.elo_service import elo_service

router = APIRouter()


class PredictionRequest(BaseModel):
    sport: str = "football"
    home_team_id: str
    away_team_id: str
    home_avg_goals_scored: float = 1.5
    home_avg_goals_conceded: float = 1.2
    away_avg_goals_scored: float = 1.3
    away_avg_goals_conceded: float = 1.4


class SmartPredictionRequest(BaseModel):
    home_team_id: int
    away_team_id: int
    match_date: Optional[str] = None


@router.post("/full-analysis")
def full_analysis(req: PredictionRequest):
    ml_result = football_trainer.predict(int(req.home_team_id), int(req.away_team_id))

    if "error" in ml_result:
        ml_result = {
            "prediction": "unknown",
            "confidence": 0,
            "probabilities": {"home_win": 0.4, "draw": 0.3, "away_win": 0.3},
            "model": "fallback",
        }

    poisson_result = poisson_service.predict_match(
        req.home_avg_goals_scored,
        req.home_avg_goals_conceded,
        req.away_avg_goals_scored,
        req.away_avg_goals_conceded,
    )

    elo_result = elo_service.predict_match(req.home_team_id, req.away_team_id)

    combined_home = (
        ml_result["probabilities"]["home_win"] * 0.5
        + poisson_result["home_win_prob"] * 0.3
        + elo_result["home_win_prob"] * 0.2
    )
    combined_away = (
        ml_result["probabilities"]["away_win"] * 0.5
        + poisson_result["away_win_prob"] * 0.3
        + elo_result["away_win_prob"] * 0.2
    )
    combined_draw = 1 - combined_home - combined_away

    return {
        "sport": req.sport,
        "models": {
            "machine_learning": ml_result,
            "poisson": poisson_result,
            "elo": elo_result,
        },
        "combined_prediction": {
            "home_win_prob": round(combined_home, 4),
            "draw_prob": round(max(0, combined_draw), 4),
            "away_win_prob": round(combined_away, 4),
            "recommended": (
                "home" if combined_home > combined_away and combined_home > max(0, combined_draw)
                else "away" if combined_away > combined_home and combined_away > max(0, combined_draw)
                else "draw"
            ),
            "confidence": round(max(combined_home, combined_away, max(0, combined_draw)), 4),
        },
    }


@router.post("/smart-predict")
def smart_predict(req: SmartPredictionRequest):
    result = football_trainer.predict(req.home_team_id, req.away_team_id, req.match_date)
    return result
