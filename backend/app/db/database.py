import sqlite3
import os
from pathlib import Path

DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DB_DIR / "jinho.db"


def get_connection() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def initialize_database():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS football_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_id INTEGER UNIQUE,
            league TEXT NOT NULL,
            season TEXT,
            match_date TEXT NOT NULL,
            home_team_id INTEGER,
            home_team_name TEXT,
            away_team_id INTEGER,
            away_team_name TEXT,
            home_score INTEGER,
            away_score INTEGER,
            home_ht_score INTEGER,
            away_ht_score INTEGER,
            status TEXT,
            collected_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS basketball_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_id INTEGER UNIQUE,
            season INTEGER,
            game_date TEXT NOT NULL,
            home_team_id INTEGER,
            home_team_name TEXT,
            away_team_id INTEGER,
            away_team_name TEXT,
            home_score INTEGER,
            away_score INTEGER,
            status TEXT,
            collected_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS elo_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id TEXT NOT NULL,
            sport TEXT NOT NULL,
            rating REAL DEFAULT 1500.0,
            updated_at TEXT DEFAULT (datetime('now')),
            UNIQUE(team_id, sport)
        );

        CREATE TABLE IF NOT EXISTS collection_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sport TEXT NOT NULL,
            league TEXT,
            season TEXT,
            matches_collected INTEGER DEFAULT 0,
            collected_at TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_football_date ON football_matches(match_date);
        CREATE INDEX IF NOT EXISTS idx_football_teams ON football_matches(home_team_id, away_team_id);
        CREATE INDEX IF NOT EXISTS idx_basketball_date ON basketball_games(game_date);
    """)
    conn.commit()
    conn.close()
