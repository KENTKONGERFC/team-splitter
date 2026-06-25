import sqlite3
import json

conn = sqlite3.connect("database/football.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    position TEXT,
    skill INTEGER
    active INTEGER DEFAULT 1
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_date TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS match_players (
    match_id INTEGER,
    player_name TEXT,
    team TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS teammate_history (
    player1 TEXT,
    player2 TEXT,
    count INTEGER DEFAULT 0,
    PRIMARY KEY(player1, player2)
)
""")

with open("players.json", encoding="utf-8") as f:
    players = json.load(f)

for p in players:
    cur.execute("""
        INSERT OR IGNORE INTO players
        (name,position,skill)
        VALUES (?,?,?)
    """,(p["name"],p["position"],p["skill"]))

conn.commit()
conn.close()

print("Database initialized")