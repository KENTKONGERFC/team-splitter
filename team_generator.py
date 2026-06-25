import sqlite3

def history_penalty(team):

    conn = sqlite3.connect(
        "database/football.db"
    )

    total = 0

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
                total += row[0]

    conn.close()

    return total

def team_score(team_a, team_b):

    skill_a = sum(p["skill"] for p in team_a)
    skill_b = sum(p["skill"] for p in team_b)

    skill_diff = abs(skill_a - skill_b)

    keeper_a = 0
    keeper_b = 0
    
    defence_a = 0
    defence_b = 0

    attack_a = 0
    attack_b = 0

    for p in team_a:

        pos = p["position"].lower()

        if pos == "keeper":
            keeper_a += 1
            
        elif pos == "defence":
            defence_a += 1

        elif pos == "attack":
            attack_a += 1

        elif pos == "both":
            defence_a += 1
            attack_a += 1  

    for p in team_b:

        pos = p["position"].lower()

        if pos == "keeper":
            keeper_b += 1
            
        elif pos == "defence":
            defence_b += 1

        elif pos == "attack":
            attack_b += 1

        elif pos == "both":
            defence_b += 1
            attack_b += 1    

    position_diff = (
        abs(defence_a - defence_b)
        +
        abs(attack_a - attack_b)
        +
        abs(keeper_a - keeper_b)
    )

    history_diff = (
    history_penalty(team_a)
    +
    history_penalty(team_b)
    )

    return (
        skill_diff * 70
        +
        position_diff * 20
        +
        history_diff * 10
    )

def generate_teams(players):

    players = sorted(
        players,
        key=lambda x: x["skill"],
        reverse=True
    )

    team_a = []
    team_b = []

    skill_a = 0
    skill_b = 0

    # Keeper 先分開
    keepers = [p for p in players if p["position"] == "keeper"]
    others = [p for p in players if p["position"] != "keeper"]

    if len(keepers) >= 2:
        team_a.append(keepers[0])
        team_b.append(keepers[1])

        skill_a += keepers[0]["skill"]
        skill_b += keepers[1]["skill"]

    elif len(keepers) == 1:
        team_a.append(keepers[0])
        skill_a += keepers[0]["skill"]

    # 其餘人按能力補入較弱隊
    for p in others:

        if len(team_a) > len(team_b):
            team_b.append(p)
            skill_b += p["skill"]

        elif len(team_b) > len(team_a):
            team_a.append(p)
            skill_a += p["skill"]

        else:

            if skill_a <= skill_b:
                team_a.append(p)
                skill_a += p["skill"]
            else:
                team_b.append(p)
                skill_b += p["skill"]

    best_a = team_a[:]
    best_b = team_b[:]

    best_score = team_score(
        best_a,
        best_b
    )

    import random

    for _ in range(1000):

        test_a = best_a[:]
        test_b = best_b[:]

        if len(test_a) == 0:
            continue

        if len(test_b) == 0:
            continue

        player_a = random.choice(test_a)
        player_b = random.choice(test_b)

        index_a = test_a.index(player_a)
        index_b = test_b.index(player_b)

        test_a[index_a] = player_b
        test_b[index_b] = player_a

        score = team_score(
            test_a,
            test_b
        )

        if score < best_score:

            best_score = score

            best_a = test_a
            best_b = test_b
    
    return best_a, best_b