import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, log_loss, brier_score_loss
from sklearn.preprocessing import StandardScaler
from app.db.database import get_connection
from app.ml.features import football_feature_extractor

MODELS_DIR = Path(__file__).parent.parent.parent / "data" / "models"


class FootballTrainer:
    def __init__(self):
        self.feature_names = []
        self.models = {}
        self.scaler = StandardScaler()
        self.meta_learner = None
        self.is_trained = False

    def build_dataset(self) -> tuple:
        conn = get_connection()
        matches = conn.execute("""
            SELECT * FROM football_matches
            WHERE home_score IS NOT NULL AND away_score IS NOT NULL
            ORDER BY match_date ASC
        """).fetchall()
        conn.close()

        X_rows = []
        y_rows = []
        dates = []

        for i, match in enumerate(matches):
            if i < 20:
                continue

            features = football_feature_extractor.compute_features(
                match["home_team_id"],
                match["away_team_id"],
                match["match_date"]
            )

            if not features:
                continue

            if match["home_score"] > match["away_score"]:
                outcome = 2  # home win
            elif match["home_score"] == match["away_score"]:
                outcome = 1  # draw
            else:
                outcome = 0  # away win

            X_rows.append(features)
            y_rows.append(outcome)
            dates.append(match["match_date"])

        if not X_rows:
            return None, None, None

        df = pd.DataFrame(X_rows)
        self.feature_names = list(df.columns)
        X = df.values.astype(np.float32)
        y = np.array(y_rows)
        dates = np.array(dates)

        return X, y, dates

    def train(self) -> dict:
        print("Building dataset...")
        X, y, dates = self.build_dataset()

        if X is None or len(X) < 100:
            return {"error": "Not enough data", "samples": 0 if X is None else len(X)}

        print(f"Dataset: {len(X)} samples, {X.shape[1]} features")

        split_idx = int(len(X) * 0.7)
        cal_idx = int(len(X) * 0.85)

        X_train, y_train = X[:split_idx], y[:split_idx]
        X_cal, y_cal = X[split_idx:cal_idx], y[split_idx:cal_idx]
        X_test, y_test = X[cal_idx:], y[cal_idx:]

        print(f"Split: train={len(X_train)}, cal={len(X_cal)}, test={len(X_test)}")

        self.scaler.fit(X_train)
        X_train_s = self.scaler.transform(X_train)
        X_cal_s = self.scaler.transform(X_cal)
        X_test_s = self.scaler.transform(X_test)

        base_models = {
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42
            ),
            "hist_gradient_boosting": HistGradientBoostingClassifier(
                max_iter=200, max_depth=6, learning_rate=0.1, random_state=42
            ),
            "random_forest": RandomForestClassifier(
                n_estimators=200, max_depth=10, random_state=42
            ),
        }

        print("Training base models...")
        meta_features_cal = []
        meta_features_test = []

        for name, model in base_models.items():
            print(f"  Training {name}...")
            model.fit(X_train_s, y_train)
            self.models[name] = model

            cal_proba = model.predict_proba(X_cal_s)
            test_proba = model.predict_proba(X_test_s)
            meta_features_cal.append(cal_proba)
            meta_features_test.append(test_proba)

            acc = accuracy_score(y_test, model.predict(X_test_s))
            print(f"    {name} accuracy: {acc:.4f}")

        print("Training meta-learner (stacking)...")
        meta_X_cal = np.hstack(meta_features_cal)
        meta_X_test = np.hstack(meta_features_test)

        self.meta_learner = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
        self.meta_learner.fit(meta_X_cal, y_cal)

        meta_pred = self.meta_learner.predict(meta_X_test)
        meta_proba = self.meta_learner.predict_proba(meta_X_test)

        ensemble_acc = accuracy_score(y_test, meta_pred)
        ensemble_logloss = log_loss(y_test, meta_proba)

        print(f"\nEnsemble accuracy: {ensemble_acc:.4f}")
        print(f"Ensemble log loss: {ensemble_logloss:.4f}")

        self.is_trained = True
        self._save_models()

        metrics = {
            "samples_total": len(X),
            "samples_train": len(X_train),
            "samples_test": len(X_test),
            "features_count": X.shape[1],
            "feature_names": self.feature_names,
            "ensemble_accuracy": round(ensemble_acc, 4),
            "ensemble_log_loss": round(ensemble_logloss, 4),
            "individual_models": {},
        }

        for name, model in self.models.items():
            pred = model.predict(X_test_s)
            proba = model.predict_proba(X_test_s)
            metrics["individual_models"][name] = {
                "accuracy": round(accuracy_score(y_test, pred), 4),
                "log_loss": round(log_loss(y_test, proba), 4),
            }

        return metrics

    def predict(self, home_team_id: int, away_team_id: int, match_date: str = None) -> dict:
        if not self.is_trained:
            self._load_models()

        if not self.is_trained:
            return {"error": "Models not trained yet"}

        features = football_feature_extractor.compute_features(home_team_id, away_team_id, match_date)
        X = np.array([list(features.values())]).astype(np.float32)
        X_s = self.scaler.transform(X)

        meta_features = []
        individual_predictions = {}

        for name, model in self.models.items():
            proba = model.predict_proba(X_s)[0]
            meta_features.append(proba)
            individual_predictions[name] = {
                "away_win": round(float(proba[0]), 4),
                "draw": round(float(proba[1]), 4),
                "home_win": round(float(proba[2]), 4),
            }

        meta_X = np.hstack(meta_features).reshape(1, -1)
        ensemble_proba = self.meta_learner.predict_proba(meta_X)[0]

        labels = ["away_win", "draw", "home_win"]
        prediction = labels[np.argmax(ensemble_proba)]

        return {
            "prediction": prediction,
            "confidence": round(float(max(ensemble_proba)), 4),
            "probabilities": {
                "away_win": round(float(ensemble_proba[0]), 4),
                "draw": round(float(ensemble_proba[1]), 4),
                "home_win": round(float(ensemble_proba[2]), 4),
            },
            "individual_models": individual_predictions,
            "features_used": self.feature_names,
            "model": "stacking_ensemble",
        }

    def _save_models(self):
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "models": self.models,
            "scaler": self.scaler,
            "meta_learner": self.meta_learner,
            "feature_names": self.feature_names,
        }, MODELS_DIR / "football_ensemble.joblib")
        print(f"Models saved to {MODELS_DIR / 'football_ensemble.joblib'}")

    def _load_models(self):
        model_path = MODELS_DIR / "football_ensemble.joblib"
        if model_path.exists():
            data = joblib.load(model_path)
            self.models = data["models"]
            self.scaler = data["scaler"]
            self.meta_learner = data["meta_learner"]
            self.feature_names = data["feature_names"]
            self.is_trained = True
            return True
        return False


football_trainer = FootballTrainer()
