import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from typing import Optional


class MatchPredictor:
    def __init__(self):
        self.models = {
            "random_forest": RandomForestClassifier(
                n_estimators=200, max_depth=10, random_state=42
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=150, max_depth=5, learning_rate=0.1, random_state=42
            ),
        }
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names: list[str] = []

    def prepare_features(self, match_data: dict) -> np.ndarray:
        features = [
            match_data.get("home_elo", 1500),
            match_data.get("away_elo", 1500),
            match_data.get("home_form", 0.5),
            match_data.get("away_form", 0.5),
            match_data.get("home_avg_goals_scored", 1.5),
            match_data.get("home_avg_goals_conceded", 1.2),
            match_data.get("away_avg_goals_scored", 1.3),
            match_data.get("away_avg_goals_conceded", 1.4),
            match_data.get("h2h_home_wins", 0),
            match_data.get("h2h_draws", 0),
            match_data.get("h2h_away_wins", 0),
            match_data.get("home_days_rest", 7),
            match_data.get("away_days_rest", 7),
        ]
        self.feature_names = [
            "home_elo", "away_elo", "home_form", "away_form",
            "home_avg_scored", "home_avg_conceded",
            "away_avg_scored", "away_avg_conceded",
            "h2h_home_wins", "h2h_draws", "h2h_away_wins",
            "home_rest_days", "away_rest_days",
        ]
        return np.array(features).reshape(1, -1)

    def train(self, X: np.ndarray, y: np.ndarray):
        X_scaled = self.scaler.fit_transform(X)
        for model in self.models.values():
            model.fit(X_scaled, y)
        self.is_trained = True

    def predict(self, match_data: dict, model_name: str = "gradient_boosting") -> dict:
        features = self.prepare_features(match_data)

        if not self.is_trained:
            return self._heuristic_prediction(match_data)

        X_scaled = self.scaler.transform(features)
        model = self.models[model_name]
        probabilities = model.predict_proba(X_scaled)[0]
        prediction = model.predict(X_scaled)[0]

        labels = ["away_win", "draw", "home_win"]
        return {
            "prediction": labels[prediction],
            "confidence": float(max(probabilities)),
            "probabilities": {
                "home_win": float(probabilities[2]) if len(probabilities) > 2 else 0,
                "draw": float(probabilities[1]) if len(probabilities) > 1 else 0,
                "away_win": float(probabilities[0]),
            },
            "model_name": model_name,
            "features_used": self.feature_names,
        }

    def _heuristic_prediction(self, match_data: dict) -> dict:
        home_elo = match_data.get("home_elo", 1500)
        away_elo = match_data.get("away_elo", 1500)
        home_form = match_data.get("home_form", 0.5)
        away_form = match_data.get("away_form", 0.5)

        elo_diff = (home_elo - away_elo + 100) / 400
        form_diff = home_form - away_form

        combined = elo_diff * 0.6 + form_diff * 0.4
        home_prob = 1 / (1 + 10 ** (-combined))
        away_prob = 1 - home_prob
        draw_prob = 0.25 * (1 - abs(home_prob - away_prob))
        home_prob = home_prob * (1 - draw_prob)
        away_prob = away_prob * (1 - draw_prob)

        probs = {"home_win": home_prob, "draw": draw_prob, "away_win": away_prob}
        prediction = max(probs, key=probs.get)

        return {
            "prediction": prediction,
            "confidence": max(probs.values()),
            "probabilities": {k: round(v, 4) for k, v in probs.items()},
            "model_name": "heuristic",
            "features_used": ["elo_rating", "recent_form"],
        }

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> dict:
        results = {}
        X_scaled = self.scaler.transform(X) if self.is_trained else X
        for name, model in self.models.items():
            scores = cross_val_score(model, X_scaled, y, cv=5, scoring="accuracy")
            results[name] = {
                "mean_accuracy": round(scores.mean(), 4),
                "std": round(scores.std(), 4),
            }
        return results


predictor = MatchPredictor()
