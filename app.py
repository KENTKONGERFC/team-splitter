from flask import *
import sqlite3
import json
import os
from datetime import datetime

from team_generator import generate_teams

app = Flask(__name__)
app.secret_key = "football-secret"

USERNAME = "admin"
PASSWORD = "admin"

def get_db():

    db_path = os.path.join(
        "/data", "football.db"
    )

    print("DB PATH =", db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    return conn


@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == USERNAME and password == PASSWORD:
            session["login"] = True
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if not session.get("login"):
        return redirect("/")

    conn = get_db()

    players = conn.execute("""
        SELECT *
        FROM players
        WHERE active = 1
        ORDER BY name COLLATE NOCASE
    """).fetchall()

    return render_template(
        "dashboard.html",
        players=players
    )

@app.route("/generate", methods=["POST"])
def generate():

    if not session.get("login"):
        return redirect("/")

    conn = get_db()

    ids = request.form.getlist("players")

    players = []

    for pid in ids:

        row = conn.execute(
            "SELECT * FROM players WHERE id=?",
            (pid,)
        ).fetchone()

        if row:

            players.append({
                "name": row["name"],
                "position": row["position"],
                "skill": row["skill"]
            })

    # Guest Players

    for i in range(1,5):

        name = request.form.get(f"guest_name_{i}")

        if name:

            players.append({
                "name": name,
                "position": request.form.get(
                    f"guest_position_{i}"
                ),
                "skill": int(
                    request.form.get(
                        f"guest_skill_{i}"
                    ) or 1
                )
            })

    team_a, team_b = generate_teams(players)

    team_a = sorted(
    team_a,
    key=lambda x: x["name"].lower()
    )

    team_b = sorted(
    team_b,
    key=lambda x: x["name"].lower()
    )

    skill_a = sum(x["skill"] for x in team_a)
    skill_b = sum(x["skill"] for x in team_b)

    def team_stats(team):

        keeper = 0
        defence = 0
        attack = 0
        both = 0

        for p in team:

            pos = p["position"].lower()

            if pos == "keeper":
                keeper += 1

            elif pos == "defence":
                defence += 1

            elif pos == "attack":
                attack += 1

            elif pos == "both":
                both += 1

        return {
            "players": len(team),
            "keeper": keeper,
            "defence": defence,
            "attack": attack,
            "both": both
        }

    stats_a = team_stats(team_a)
    stats_b = team_stats(team_b)

    return render_template(
        "result.html",
        team_a=team_a,
        team_b=team_b,
        skill_a=skill_a,
        skill_b=skill_b,
        stats_a=stats_a,
        stats_b=stats_b
    )

import json
from datetime import datetime

@app.route("/generate_again", methods=["POST"])
def generate_again():

    if not session.get("login"):
        return redirect("/")

    team_a = json.loads(
        request.form["team_a"]
    )

    team_b = json.loads(
        request.form["team_b"]
    )

    players = team_a + team_b

    team_a, team_b = generate_teams(players)

    team_a = sorted(
        team_a,
        key=lambda x: x["name"].lower()
    )

    team_b = sorted(
        team_b,
        key=lambda x: x["name"].lower()
    )

    skill_a = sum(
        x["skill"] for x in team_a
    )

    skill_b = sum(
        x["skill"] for x in team_b
    )

    def team_stats(team):

        keeper = 0
        defence = 0
        attack = 0
        both = 0

        for p in team:

            pos = p["position"].lower()

            if pos == "keeper":
                keeper += 1

            elif pos == "defence":
                defence += 1

            elif pos == "attack":
                attack += 1

            elif pos == "both":
                both += 1

        return {
            "players": len(team),
            "keeper": keeper,
            "defence": defence,
            "attack": attack,
            "both": both
        }

    stats_a = team_stats(team_a)
    stats_b = team_stats(team_b)

    return render_template(
        "result.html",
        team_a=team_a,
        team_b=team_b,
        skill_a=skill_a,
        skill_b=skill_b,
        stats_a=stats_a,
        stats_b=stats_b
    )

@app.route("/confirm", methods=["POST"])
def confirm_teams():

    if not session.get("login"):
        return redirect("/")

    conn = get_db()

    team_a = json.loads(
        request.form["team_a"]
    )

    team_b = json.loads(
        request.form["team_b"]
    )

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    cur = conn.cursor()

    cur.execute(
        "INSERT INTO matches (match_date) VALUES (?)",
        (today,)
    )

    match_id = cur.lastrowid

    for player in team_a:

        cur.execute("""
            INSERT INTO match_players
            (match_id, player_name, team)
            VALUES (?, ?, ?)
        """,
        (
            match_id,
            player["name"],
            "Blue"
        ))

    for player in team_b:

        cur.execute("""
            INSERT INTO match_players
            (match_id, player_name, team)
            VALUES (?, ?, ?)
        """,
        (
            match_id,
            player["name"],
            "White"
        ))


    def update_history(team):

        names = []

        for p in team:
            names.append(
                p["name"]
            )

        names.sort()

        for i in range(len(names)):

            for j in range(i + 1, len(names)):

                p1 = names[i]
                p2 = names[j]

                row = conn.execute("""
                    SELECT count
                    FROM teammate_history
                    WHERE player1=?
                    AND player2=?
                """,
                (p1, p2)
                ).fetchone()

                if row:

                    conn.execute("""
                        UPDATE teammate_history
                        SET count=count+1
                        WHERE player1=?
                        AND player2=?
                    """,
                    (p1, p2)
                    )

                else:

                    conn.execute("""
                        INSERT INTO teammate_history
                        (
                            player1,
                            player2,
                            count
                        )
                        VALUES (?, ?, 1)
                    """,
                    (p1, p2)
                    )

    update_history(team_a)
    update_history(team_b)

    conn.commit()

    return redirect("/history")

@app.route("/players")
def players():

    if not session.get("login"):
        return redirect("/")

    conn = get_db()

    players = conn.execute("""
        SELECT *
        FROM players
        ORDER BY name COLLATE NOCASE
    """).fetchall()

    return render_template(
        "players.html",
        players=players
    )

@app.route("/history")
def history():

    if not session.get("login"):
        return redirect("/")

    conn = get_db()

    matches = conn.execute("""
        SELECT *
        FROM matches
        ORDER BY id DESC
    """).fetchall()

    history_data = []

    for match in matches:

        players = conn.execute("""
            SELECT *
            FROM match_players
            WHERE match_id=?
        """,
        (match["id"],)
        ).fetchall()

        blue = []
        white = []

        for p in players:

            if p["team"] == "Blue":
                blue.append(
                    p["player_name"]
                )
            else:
                white.append(
                    p["player_name"]
                )

        blue.sort(key=str.lower)
        white.sort(key=str.lower)
        
        history_data.append({
            "date": match["match_date"],
            "blue": blue,
            "white": white
        })

    return render_template(
        "history.html",
        history=history_data
    )

@app.route("/ranking")
def ranking():

    if not session.get("login"):
        return redirect("/")

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM teammate_history
        ORDER BY count DESC
        LIMIT 50
    """).fetchall()

    return render_template(
        "ranking.html",
        rows=rows
    )

@app.route(
    "/add_player",
    methods=["GET", "POST"]
)
def add_player():

    if not session.get("login"):
        return redirect("/")

    conn = get_db()

    if request.method == "POST":

        name = request.form["name"]

        position = request.form["position"]

        skill = request.form["skill"]

        conn.execute("""
            INSERT INTO players
            (name, position, skill), active
            VALUES (?, ?, ?, 1)
        """,
        (
            name,
            position,
            skill
        ))

        conn.commit()

        return redirect("/players")

    return render_template(
        "add_player.html"
    )

@app.route(
    "/edit_player/<int:player_id>",
    methods=["GET","POST"]
)
def edit_player(player_id):

    if not session.get("login"):
        return redirect("/")

    conn = get_db()

    if request.method == "POST":

        name = request.form["name"]

        position = request.form["position"]

        skill = request.form["skill"]

        conn.execute("""
            UPDATE players
            SET
                name=?,
                position=?,
                skill=?
            WHERE id=?
        """,
        (
            name,
            position,
            skill,
            player_id
        ))

        conn.commit()

        return redirect("/players")

    player = conn.execute("""
        SELECT *
        FROM players
        WHERE id=?
    """,
    (player_id,)
    ).fetchone()

    return render_template(
        "edit_player.html",
        player=player
    )

@app.route("/deactivate_player/<int:player_id>")
def deactivate_player(player_id):

    if not session.get("login"):
        return redirect("/")

    conn = get_db()

    conn.execute("""
        UPDATE players
        SET active=0
        WHERE id=?
    """,
    (player_id,)
    )

    conn.commit()

    return redirect("/players")

@app.route("/activate_player/<int:player_id>")
def activate_player(player_id):

    if not session.get("login"):
        return redirect("/")

    conn = get_db()

    conn.execute("""
        UPDATE players
        SET active=1
        WHERE id=?
    """,
    (player_id,)
    )

    conn.commit()

    return redirect("/players")

if __name__ == "__main__":
    app.run(debug=True)
    
