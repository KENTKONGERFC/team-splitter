def team_score(team_a, team_b):

    skill_a = sum(p["skill"] for p in team_a)
    skill_b = sum(p["skill"] for p in team_b)

    skill_diff = abs(skill_a - skill_b)

    defence_a = 0
    defence_b = 0

    attack_a = 0
    attack_b = 0

    for p in team_a:

        pos = p["position"].lower()

        if pos == "defence":
            defence_a += 1

        elif pos == "attack":
            attack_a += 1

        elif pos == "both":
            defence_a += 1
            attack_a += 1

    for p in team_b:

        pos = p["position"].lower()

        if pos == "defence":
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
    )

    return (
        skill_diff * 70
        +
        position_diff * 20
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

    return team_a, team_b