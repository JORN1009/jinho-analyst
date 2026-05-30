from fastapi import APIRouter, Query

router = APIRouter()

MOCK_PLAYERS = [
    {"id": "1", "name": "Novak Djokovic", "ranking": 1, "elo": 2150, "surface_pref": "hard"},
    {"id": "2", "name": "Carlos Alcaraz", "ranking": 2, "elo": 2100, "surface_pref": "clay"},
    {"id": "3", "name": "Jannik Sinner", "ranking": 3, "elo": 2080, "surface_pref": "hard"},
    {"id": "4", "name": "Daniil Medvedev", "ranking": 4, "elo": 2020, "surface_pref": "hard"},
]

SURFACE_BONUS = {"clay": 50, "hard": 30, "grass": 40}


@router.get("/players")
def get_players():
    return {"players": MOCK_PLAYERS}


@router.post("/predict")
def predict_match(
    player_a_id: str,
    player_b_id: str,
    surface: str = Query(default="hard"),
):
    player_a = next((p for p in MOCK_PLAYERS if p["id"] == player_a_id), None)
    player_b = next((p for p in MOCK_PLAYERS if p["id"] == player_b_id), None)

    if not player_a or not player_b:
        return {"error": "Player not found"}

    elo_a = player_a["elo"]
    elo_b = player_b["elo"]

    if player_a["surface_pref"] == surface:
        elo_a += SURFACE_BONUS.get(surface, 0)
    if player_b["surface_pref"] == surface:
        elo_b += SURFACE_BONUS.get(surface, 0)

    prob_a = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
    prob_b = 1 - prob_a

    return {
        "player_a": player_a["name"],
        "player_b": player_b["name"],
        "surface": surface,
        "prob_a_wins": round(prob_a, 4),
        "prob_b_wins": round(prob_b, 4),
        "predicted_winner": player_a["name"] if prob_a > prob_b else player_b["name"],
        "confidence": round(max(prob_a, prob_b), 4),
    }
