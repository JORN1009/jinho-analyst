from fastapi import APIRouter, Query
from app.services.data_fetcher import data_fetcher
from app.services.elo_service import elo_service
from app.services.poisson_service import poisson_service

router = APIRouter()

LEAGUES = {
    "PL": "Premier League",
    "PD": "La Liga",
    "BL1": "Bundesliga",
    "SA": "Serie A",
    "FL1": "Ligue 1",
    "CL": "Champions League",
}


@router.get("/leagues")
def get_leagues():
    return [{"code": k, "name": v} for k, v in LEAGUES.items()]


@router.get("/matches")
async def get_matches(league: str = Query(default="PL")):
    matches = await data_fetcher.get_football_matches(league)
    return {"league": league, "matches": matches}


@router.get("/standings")
async def get_standings(league: str = Query(default="PL")):
    standings = await data_fetcher.get_football_standings(league)
    return {"league": league, "standings": standings}


@router.get("/team/{team_id}/form")
async def get_team_form(team_id: int, limit: int = Query(default=10)):
    matches = await data_fetcher.get_football_team_matches(team_id, limit)
    form = []
    goals_scored = 0
    goals_conceded = 0

    for match in matches:
        home_team = match.get("homeTeam", {})
        score = match.get("score", {}).get("fullTime", {})
        home_goals = score.get("home", 0)
        away_goals = score.get("away", 0)

        if home_team.get("id") == team_id:
            goals_scored += home_goals
            goals_conceded += away_goals
            if home_goals > away_goals:
                form.append("W")
            elif home_goals == away_goals:
                form.append("D")
            else:
                form.append("L")
        else:
            goals_scored += away_goals
            goals_conceded += home_goals
            if away_goals > home_goals:
                form.append("W")
            elif away_goals == home_goals:
                form.append("D")
            else:
                form.append("L")

    n = len(matches) or 1
    return {
        "team_id": team_id,
        "form": form,
        "matches_analyzed": n,
        "avg_goals_scored": round(goals_scored / n, 2),
        "avg_goals_conceded": round(goals_conceded / n, 2),
        "win_rate": round(form.count("W") / n, 2),
    }


@router.post("/predict/poisson")
async def predict_poisson(
    home_avg_scored: float,
    home_avg_conceded: float,
    away_avg_scored: float,
    away_avg_conceded: float,
):
    result = poisson_service.predict_match(
        home_avg_scored, home_avg_conceded, away_avg_scored, away_avg_conceded
    )
    return result


@router.post("/predict/elo")
async def predict_elo(home_team_id: str, away_team_id: str):
    result = elo_service.predict_match(home_team_id, away_team_id)
    return result
