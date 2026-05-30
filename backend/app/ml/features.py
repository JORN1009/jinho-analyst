from app.db.database import get_connection
from datetime import datetime, timedelta


class FootballFeatureExtractor:
    def compute_features(self, home_team_id: int, away_team_id: int, cutoff_date: str = None) -> dict:
        if cutoff_date is None:
            cutoff_date = datetime.now().isoformat()

        conn = get_connection()

        home_matches = conn.execute("""
            SELECT * FROM football_matches
            WHERE (home_team_id = ? OR away_team_id = ?) AND match_date < ?
            ORDER BY match_date DESC LIMIT 20
        """, (home_team_id, home_team_id, cutoff_date)).fetchall()

        away_matches = conn.execute("""
            SELECT * FROM football_matches
            WHERE (home_team_id = ? OR away_team_id = ?) AND match_date < ?
            ORDER BY match_date DESC LIMIT 20
        """, (away_team_id, away_team_id, cutoff_date)).fetchall()

        h2h_matches = conn.execute("""
            SELECT * FROM football_matches
            WHERE ((home_team_id = ? AND away_team_id = ?) OR (home_team_id = ? AND away_team_id = ?))
            AND match_date < ?
            ORDER BY match_date DESC LIMIT 10
        """, (home_team_id, away_team_id, away_team_id, home_team_id, cutoff_date)).fetchall()

        conn.close()

        features = {}
        features.update(self._team_features(home_matches, home_team_id, "home"))
        features.update(self._team_features(away_matches, away_team_id, "away"))
        features.update(self._h2h_features(h2h_matches, home_team_id, away_team_id))
        features.update(self._derived_features(features))

        return features

    def _team_features(self, matches, team_id, prefix) -> dict:
        if not matches:
            return self._default_team_features(prefix)

        last_5 = matches[:5]
        last_10 = matches[:10]

        goals_scored_5, goals_conceded_5 = 0, 0
        goals_scored_10, goals_conceded_10 = 0, 0
        wins_5, draws_5, losses_5 = 0, 0, 0
        wins_10, draws_10 = 0, 0
        home_wins, home_games = 0, 0
        away_wins, away_games = 0, 0
        clean_sheets_5 = 0

        for i, m in enumerate(last_10):
            is_home = m["home_team_id"] == team_id
            scored = m["home_score"] if is_home else m["away_score"]
            conceded = m["away_score"] if is_home else m["home_score"]

            if scored is None or conceded is None:
                continue

            if i < 5:
                goals_scored_5 += scored
                goals_conceded_5 += conceded
                if conceded == 0:
                    clean_sheets_5 += 1
                if scored > conceded:
                    wins_5 += 1
                elif scored == conceded:
                    draws_5 += 1
                else:
                    losses_5 += 1

            goals_scored_10 += scored
            goals_conceded_10 += conceded
            if scored > conceded:
                wins_10 += 1
            elif scored == conceded:
                draws_10 += 1

            if is_home:
                home_games += 1
                if scored > conceded:
                    home_wins += 1
            else:
                away_games += 1
                if scored > conceded:
                    away_wins += 1

        n5 = min(len(last_5), 5) or 1
        n10 = min(len(last_10), 10) or 1

        form_5 = (wins_5 * 3 + draws_5) / (n5 * 3)
        form_10 = (wins_10 * 3 + draws_10) / (n10 * 3)

        return {
            f"{prefix}_form_5": round(form_5, 4),
            f"{prefix}_form_10": round(form_10, 4),
            f"{prefix}_win_rate_5": round(wins_5 / n5, 4),
            f"{prefix}_avg_scored_5": round(goals_scored_5 / n5, 4),
            f"{prefix}_avg_conceded_5": round(goals_conceded_5 / n5, 4),
            f"{prefix}_avg_scored_10": round(goals_scored_10 / n10, 4),
            f"{prefix}_avg_conceded_10": round(goals_conceded_10 / n10, 4),
            f"{prefix}_clean_sheets_5": clean_sheets_5,
            f"{prefix}_home_win_rate": round(home_wins / home_games, 4) if home_games > 0 else 0.4,
            f"{prefix}_away_win_rate": round(away_wins / away_games, 4) if away_games > 0 else 0.3,
            f"{prefix}_goal_diff_5": goals_scored_5 - goals_conceded_5,
            f"{prefix}_goal_diff_10": goals_scored_10 - goals_conceded_10,
        }

    def _default_team_features(self, prefix) -> dict:
        return {
            f"{prefix}_form_5": 0.5,
            f"{prefix}_form_10": 0.5,
            f"{prefix}_win_rate_5": 0.33,
            f"{prefix}_avg_scored_5": 1.3,
            f"{prefix}_avg_conceded_5": 1.3,
            f"{prefix}_avg_scored_10": 1.3,
            f"{prefix}_avg_conceded_10": 1.3,
            f"{prefix}_clean_sheets_5": 1,
            f"{prefix}_home_win_rate": 0.4,
            f"{prefix}_away_win_rate": 0.3,
            f"{prefix}_goal_diff_5": 0,
            f"{prefix}_goal_diff_10": 0,
        }

    def _h2h_features(self, matches, home_team_id, away_team_id) -> dict:
        if not matches:
            return {"h2h_home_wins_pct": 0.4, "h2h_draws_pct": 0.3, "h2h_total": 0, "h2h_avg_goals": 2.5}

        home_wins, draws, total_goals = 0, 0, 0
        for m in matches:
            hs = m["home_score"] or 0
            aws = m["away_score"] or 0
            total_goals += hs + aws

            if m["home_team_id"] == home_team_id:
                if hs > aws:
                    home_wins += 1
                elif hs == aws:
                    draws += 1
            else:
                if aws > hs:
                    home_wins += 1
                elif hs == aws:
                    draws += 1

        n = len(matches)
        return {
            "h2h_home_wins_pct": round(home_wins / n, 4),
            "h2h_draws_pct": round(draws / n, 4),
            "h2h_total": n,
            "h2h_avg_goals": round(total_goals / n, 4),
        }

    def _derived_features(self, features) -> dict:
        form_diff = features.get("home_form_5", 0.5) - features.get("away_form_5", 0.5)
        attack_diff = features.get("home_avg_scored_5", 1.3) - features.get("away_avg_scored_5", 1.3)
        defense_diff = features.get("away_avg_conceded_5", 1.3) - features.get("home_avg_conceded_5", 1.3)

        return {
            "form_diff": round(form_diff, 4),
            "attack_diff": round(attack_diff, 4),
            "defense_diff": round(defense_diff, 4),
            "home_attack_vs_away_defense": round(
                features.get("home_avg_scored_5", 1.3) * features.get("away_avg_conceded_5", 1.3) / 1.3, 4
            ),
            "away_attack_vs_home_defense": round(
                features.get("away_avg_scored_5", 1.3) * features.get("home_avg_conceded_5", 1.3) / 1.3, 4
            ),
        }


football_feature_extractor = FootballFeatureExtractor()
