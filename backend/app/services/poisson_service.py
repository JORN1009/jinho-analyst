import numpy as np
from scipy.stats import poisson


class PoissonService:
    def predict_match(
        self,
        home_avg_scored: float,
        home_avg_conceded: float,
        away_avg_scored: float,
        away_avg_conceded: float,
        league_avg_goals: float = 2.7,
    ) -> dict:
        home_attack = home_avg_scored / league_avg_goals
        home_defense = home_avg_conceded / league_avg_goals
        away_attack = away_avg_scored / league_avg_goals
        away_defense = away_avg_conceded / league_avg_goals

        home_expected = home_attack * away_defense * league_avg_goals * 1.1
        away_expected = away_attack * home_defense * league_avg_goals * 0.9

        home_expected = max(0.3, min(home_expected, 5.0))
        away_expected = max(0.3, min(away_expected, 5.0))

        max_goals = 8
        home_probs = [poisson.pmf(i, home_expected) for i in range(max_goals)]
        away_probs = [poisson.pmf(i, away_expected) for i in range(max_goals)]

        home_win = 0.0
        draw = 0.0
        away_win = 0.0

        score_matrix = {}
        for i in range(max_goals):
            for j in range(max_goals):
                prob = home_probs[i] * away_probs[j]
                score_matrix[f"{i}-{j}"] = round(prob, 4)
                if i > j:
                    home_win += prob
                elif i == j:
                    draw += prob
                else:
                    away_win += prob

        sorted_scores = sorted(score_matrix.items(), key=lambda x: x[1], reverse=True)

        return {
            "home_goals_expected": round(home_expected, 2),
            "away_goals_expected": round(away_expected, 2),
            "home_win_prob": round(home_win, 4),
            "draw_prob": round(draw, 4),
            "away_win_prob": round(away_win, 4),
            "most_likely_scores": sorted_scores[:5],
            "over_2_5_prob": round(1 - sum(
                home_probs[i] * away_probs[j]
                for i in range(max_goals)
                for j in range(max_goals)
                if i + j <= 2
            ), 4),
            "btts_prob": round(1 - sum(
                home_probs[0] * away_probs[j] for j in range(max_goals)
            ) - sum(
                home_probs[i] * away_probs[0] for i in range(1, max_goals)
            ), 4),
        }


poisson_service = PoissonService()
