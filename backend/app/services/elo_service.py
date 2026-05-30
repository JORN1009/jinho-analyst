from datetime import datetime

K_FACTOR = 32
INITIAL_RATING = 1500
HOME_ADVANTAGE = 100


class EloService:
    def __init__(self):
        self.ratings: dict[str, float] = {}

    def get_rating(self, team_id: str) -> float:
        return self.ratings.get(team_id, INITIAL_RATING)

    def expected_score(self, rating_a: float, rating_b: float) -> float:
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    def update_ratings(self, home_id: str, away_id: str, home_score: int, away_score: int):
        home_rating = self.get_rating(home_id) + HOME_ADVANTAGE
        away_rating = self.get_rating(away_id)

        home_expected = self.expected_score(home_rating, away_rating)
        away_expected = self.expected_score(away_rating, home_rating)

        if home_score > away_score:
            home_actual, away_actual = 1.0, 0.0
        elif home_score < away_score:
            home_actual, away_actual = 0.0, 1.0
        else:
            home_actual, away_actual = 0.5, 0.5

        self.ratings[home_id] = self.get_rating(home_id) + K_FACTOR * (home_actual - home_expected)
        self.ratings[away_id] = self.get_rating(away_id) + K_FACTOR * (away_actual - away_expected)

    def predict_match(self, home_id: str, away_id: str) -> dict:
        home_rating = self.get_rating(home_id) + HOME_ADVANTAGE
        away_rating = self.get_rating(away_id)

        home_win_prob = self.expected_score(home_rating, away_rating)
        away_win_prob = self.expected_score(away_rating, home_rating)
        draw_prob = 1 - home_win_prob - away_win_prob

        if draw_prob < 0:
            draw_prob = 0.15
            remaining = 1 - draw_prob
            total = home_win_prob + away_win_prob
            home_win_prob = remaining * (home_win_prob / total)
            away_win_prob = remaining * (away_win_prob / total)

        return {
            "home_win_prob": round(home_win_prob, 4),
            "draw_prob": round(draw_prob, 4),
            "away_win_prob": round(away_win_prob, 4),
            "home_elo": round(self.get_rating(home_id), 1),
            "away_elo": round(self.get_rating(away_id), 1),
        }


elo_service = EloService()
