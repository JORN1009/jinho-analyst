from fastapi import APIRouter

router = APIRouter()

MOCK_FIGHTERS = [
    {"id": "1", "name": "Islam Makhachev", "division": "Lightweight", "elo": 1950, "style": "wrestler"},
    {"id": "2", "name": "Alex Pereira", "division": "Light Heavyweight", "elo": 1900, "style": "striker"},
    {"id": "3", "name": "Jon Jones", "division": "Heavyweight", "elo": 2000, "style": "complete"},
    {"id": "4", "name": "Ilia Topuria", "division": "Featherweight", "elo": 1880, "style": "boxer"},
]

STYLE_MATCHUP = {
    ("wrestler", "striker"): 0.1,
    ("striker", "wrestler"): -0.1,
    ("boxer", "wrestler"): -0.05,
    ("wrestler", "boxer"): 0.05,
    ("striker", "boxer"): 0.03,
    ("boxer", "striker"): -0.03,
}


@router.get("/fighters")
def get_fighters():
    return {"fighters": MOCK_FIGHTERS}


@router.post("/predict")
def predict_fight(fighter_a_id: str, fighter_b_id: str):
    fighter_a = next((f for f in MOCK_FIGHTERS if f["id"] == fighter_a_id), None)
    fighter_b = next((f for f in MOCK_FIGHTERS if f["id"] == fighter_b_id), None)

    if not fighter_a or not fighter_b:
        return {"error": "Fighter not found"}

    elo_a = fighter_a["elo"]
    elo_b = fighter_b["elo"]

    style_key = (fighter_a["style"], fighter_b["style"])
    style_modifier = STYLE_MATCHUP.get(style_key, 0)

    prob_a_base = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
    prob_a = min(0.95, max(0.05, prob_a_base + style_modifier))
    prob_b = 1 - prob_a

    return {
        "fighter_a": fighter_a["name"],
        "fighter_b": fighter_b["name"],
        "prob_a_wins": round(prob_a, 4),
        "prob_b_wins": round(prob_b, 4),
        "style_matchup": f"{fighter_a['style']} vs {fighter_b['style']}",
        "style_advantage": "A" if style_modifier > 0 else "B" if style_modifier < 0 else "neutral",
        "predicted_winner": fighter_a["name"] if prob_a > prob_b else fighter_b["name"],
        "confidence": round(max(prob_a, prob_b), 4),
    }
