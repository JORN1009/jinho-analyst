import asyncio
import httpx
import os
from datetime import datetime
from app.db.database import get_connection
from dotenv import load_dotenv

load_dotenv()

FOOTBALL_DATA_API = "https://api.football-data.org/v4"
BALLDONTLIE_API = "https://api.balldontlie.io/v1"

FOOTBALL_LEAGUES = ["PL", "PD", "BL1", "SA", "FL1"]


class DataCollector:
    def __init__(self):
        self.football_key = os.getenv("FOOTBALL_DATA_API_KEY", "")
        self.basketball_key = os.getenv("BALLDONTLIE_API_KEY", "")

    async def collect_football_season(self, league: str, season: int) -> int:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{FOOTBALL_DATA_API}/competitions/{league}/matches",
                headers={"X-Auth-Token": self.football_key},
                params={"season": season, "status": "FINISHED"},
            )

            if response.status_code != 200:
                return 0

            matches = response.json().get("matches", [])
            conn = get_connection()
            count = 0

            for match in matches:
                score = match.get("score", {}).get("fullTime", {})
                ht_score = match.get("score", {}).get("halfTime", {})
                try:
                    conn.execute("""
                        INSERT OR IGNORE INTO football_matches
                        (api_id, league, season, match_date, home_team_id, home_team_name,
                         away_team_id, away_team_name, home_score, away_score,
                         home_ht_score, away_ht_score, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        match.get("id"),
                        league,
                        str(season),
                        match.get("utcDate", ""),
                        match.get("homeTeam", {}).get("id"),
                        match.get("homeTeam", {}).get("name"),
                        match.get("awayTeam", {}).get("id"),
                        match.get("awayTeam", {}).get("name"),
                        score.get("home"),
                        score.get("away"),
                        ht_score.get("home"),
                        ht_score.get("away"),
                        match.get("status"),
                    ))
                    count += 1
                except Exception:
                    continue

            conn.execute("""
                INSERT INTO collection_log (sport, league, season, matches_collected)
                VALUES (?, ?, ?, ?)
            """, ("football", league, str(season), count))
            conn.commit()
            conn.close()
            return count

    async def collect_all_football(self, seasons: list[int] = None) -> dict:
        if seasons is None:
            seasons = [2022, 2023, 2024]

        results = {}
        for league in FOOTBALL_LEAGUES:
            results[league] = {}
            for season in seasons:
                count = await self.collect_football_season(league, season)
                results[league][season] = count
                await asyncio.sleep(6)  # respect rate limit (10 req/min)
        return results

    async def collect_basketball_season(self, season: int) -> int:
        conn = get_connection()
        count = 0
        page = 1

        async with httpx.AsyncClient(timeout=30) as client:
            while True:
                response = await client.get(
                    f"{BALLDONTLIE_API}/games",
                    headers={"Authorization": self.basketball_key},
                    params={"seasons[]": season, "per_page": 100, "page": page},
                )

                if response.status_code != 200:
                    break

                data = response.json()
                games = data.get("data", [])

                if not games:
                    break

                for game in games:
                    try:
                        conn.execute("""
                            INSERT OR IGNORE INTO basketball_games
                            (api_id, season, game_date, home_team_id, home_team_name,
                             away_team_id, away_team_name, home_score, away_score, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            game.get("id"),
                            season,
                            game.get("date", ""),
                            game.get("home_team", {}).get("id"),
                            game.get("home_team", {}).get("full_name"),
                            game.get("visitor_team", {}).get("id"),
                            game.get("visitor_team", {}).get("full_name"),
                            game.get("home_team_score"),
                            game.get("visitor_team_score"),
                            game.get("status"),
                        ))
                        count += 1
                    except Exception:
                        continue

                meta = data.get("meta", {})
                if page >= meta.get("total_pages", 1):
                    break
                page += 1
                await asyncio.sleep(1)

        conn.execute("""
            INSERT INTO collection_log (sport, league, season, matches_collected)
            VALUES (?, ?, ?, ?)
        """, ("basketball", "NBA", str(season), count))
        conn.commit()
        conn.close()
        return count

    async def collect_all_basketball(self, seasons: list[int] = None) -> dict:
        if seasons is None:
            seasons = [2022, 2023, 2024]

        results = {}
        for season in seasons:
            count = await self.collect_basketball_season(season)
            results[season] = count
        return results

    async def collect_incremental(self) -> dict:
        results = {"football": {}, "basketball": 0}
        current_season = datetime.now().year if datetime.now().month >= 8 else datetime.now().year - 1

        for league in FOOTBALL_LEAGUES:
            count = await self.collect_football_season(league, current_season)
            results["football"][league] = count
            await asyncio.sleep(6)

        results["basketball"] = await self.collect_basketball_season(current_season)
        return results

    def get_stats(self) -> dict:
        conn = get_connection()
        football_count = conn.execute("SELECT COUNT(*) FROM football_matches").fetchone()[0]
        basketball_count = conn.execute("SELECT COUNT(*) FROM basketball_games").fetchone()[0]
        last_collection = conn.execute(
            "SELECT collected_at FROM collection_log ORDER BY collected_at DESC LIMIT 1"
        ).fetchone()
        conn.close()

        return {
            "football_matches": football_count,
            "basketball_games": basketball_count,
            "last_collection": last_collection[0] if last_collection else None,
        }


data_collector = DataCollector()
