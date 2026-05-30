from fastapi import APIRouter, Query
from app.services.data_fetcher import data_fetcher

router = APIRouter()


@router.get("/games")
async def get_games(season: int = Query(default=2024)):
    games = await data_fetcher.get_basketball_games(season)
    return {"season": season, "games": games}


@router.get("/team/{team_id}/stats")
async def get_team_stats(team_id: int, season: int = Query(default=2024)):
    stats = await data_fetcher.get_basketball_stats(team_id, season)

    if not stats:
        return {"team_id": team_id, "stats": None}

    total_pts = sum(s.get("pts", 0) for s in stats)
    total_reb = sum(s.get("reb", 0) for s in stats)
    total_ast = sum(s.get("ast", 0) for s in stats)
    n = len(stats)

    return {
        "team_id": team_id,
        "season": season,
        "games_analyzed": n,
        "avg_points": round(total_pts / n, 1),
        "avg_rebounds": round(total_reb / n, 1),
        "avg_assists": round(total_ast / n, 1),
    }
