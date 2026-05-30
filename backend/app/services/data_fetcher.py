import httpx
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

FOOTBALL_DATA_API = "https://api.football-data.org/v4"
BALLDONTLIE_API = "https://api.balldontlie.io/v1"


class DataFetcher:
    def __init__(self):
        self.football_key = os.getenv("FOOTBALL_DATA_API_KEY", "")
        self.basketball_key = os.getenv("BALLDONTLIE_API_KEY", "")

    async def get_football_matches(self, league: str = "PL", days: int = 7) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FOOTBALL_DATA_API}/competitions/{league}/matches",
                headers={"X-Auth-Token": self.football_key},
                params={"status": "SCHEDULED"},
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("matches", [])
            return []

    async def get_football_standings(self, league: str = "PL") -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FOOTBALL_DATA_API}/competitions/{league}/standings",
                headers={"X-Auth-Token": self.football_key},
            )
            if response.status_code == 200:
                data = response.json()
                standings = data.get("standings", [])
                if standings:
                    return standings[0].get("table", [])
            return []

    async def get_football_team_matches(self, team_id: int, limit: int = 10) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FOOTBALL_DATA_API}/teams/{team_id}/matches",
                headers={"X-Auth-Token": self.football_key},
                params={"status": "FINISHED", "limit": limit},
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("matches", [])
            return []

    async def get_basketball_games(self, season: int = 2024) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BALLDONTLIE_API}/games",
                headers={"Authorization": self.basketball_key},
                params={"seasons[]": season, "per_page": 25},
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            return []

    async def get_basketball_stats(self, team_id: int, season: int = 2024) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BALLDONTLIE_API}/stats",
                headers={"Authorization": self.basketball_key},
                params={"seasons[]": season, "team_ids[]": team_id, "per_page": 50},
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            return []


data_fetcher = DataFetcher()
