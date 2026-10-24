"""JSON-backed local demo data. Simulated values are labelled in each record."""
import json, random
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
PLAYERS_FILE = DATA_DIR / "players.json"
TEAMS_FILE = DATA_DIR / "teams.json"
random.seed(42)

GAMES = {
    "Valorant": ["IGL", "Entry Fragger", "AWPer", "Support", "Lurker", "Flex"],
    "Counter-Strike 2": ["IGL", "Entry Fragger", "AWPer", "Support", "Lurker", "Flex"],
    "Dota 2": ["IGL / Captain", "Carry", "Support / Roamer", "Flex", "Scout"],
    "BGMI": ["Assaulter", "IGL / Captain", "Support", "Scout", "Flex"],
}
METRIC_KEYS = [
    "decision_making", "round_conversion", "coordination", "tactical_execution",
    "consistency", "opening_success", "damage_impact", "trade_efficiency",
    "survivability", "sniper_accuracy", "utility_effectiveness", "team_enablement",
    "late_round_impact", "flank_effectiveness", "adaptability", "teamfight_impact",
    "objective_control", "farm_efficiency",
]
FIRST = ["Aarav", "Ishaan", "Reyansh", "Vihaan", "Aditya", "Kabir", "Arjun", "Dev", "Rohan", "Neel",
         "Mira", "Anaya", "Saanvi", "Aadhya", "Kiara", "Ira", "Tara", "Myra", "Diya", "Zoya"]
LAST = ["Storm", "Phoenix", "Rift", "Nova", "Viper", "Shadow", "Blaze", "Frost", "Echo", "Pulse",
        "Rogue", "Spectre", "Falcon", "Orbit", "Cipher"]

def load_json(path: Path, default: Any):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def save_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def make_player(i: int) -> dict:
    game = list(GAMES)[i % len(GAMES)]
    role = GAMES[game][(i // len(GAMES)) % len(GAMES[game])]
    metrics = {key: random.randint(48, 97) for key in METRIC_KEYS}
    cost = random.randrange(150000, 1200001, 25000)
    form = [max(20, min(100, random.randint(50, 90) + j * random.randint(-3, 4))) for j in range(6)]
    return {
        "id": i + 1,
        "name": f"{FIRST[i % len(FIRST)]} {LAST[(i * 3) % len(LAST)]}",
        "handle": f"{LAST[(i * 3) % len(LAST)].lower()}_{i+17}",
        "game": game,
        "role": role,
        "region": ["India", "Southeast Asia", "Europe", "North America"][i % 4],
        "experience_years": round(random.uniform(0.5, 6.0), 1),
        "estimated_cost": cost,
        "availability": ["Available", "Available", "Contracted", "Trial"][i % 4],
        "matches_played": random.randint(24, 240),
        "win_rate": round(random.uniform(42, 72), 1),
        "kd_ratio": round(random.uniform(0.72, 1.65), 2),
        "damage_per_round": round(random.uniform(90, 185), 1),
        "metrics": metrics,
        "trend": form,
        "data_source": "SIMULATED_DEMO",
        "confidence": round(random.uniform(0.62, 0.91), 2),
        "notes": "Simulated profile for demonstration; not a real esports player.",
    }

def default_teams() -> list[dict]:
    return [
        {"id": 1, "organization": "Nova Esports Demo", "name": "Nova Valorant", "game": "Valorant",
         "competition_level": "Professional", "budget": 600000, "required_role": "IGL", "member_ids": [1, 5, 9, 13, 17]},
        {"id": 2, "organization": "Nova Esports Demo", "name": "Nova CS2 Academy", "game": "Counter-Strike 2",
         "competition_level": "Academy", "budget": 450000, "required_role": "AWPer", "member_ids": [2, 6, 10, 14, 18]},
        {"id": 3, "organization": "Nova Esports Demo", "name": "Nova Dota", "game": "Dota 2",
         "competition_level": "Semi-pro", "budget": 700000, "required_role": "Carry", "member_ids": [3, 7, 11, 15, 19]},
        {"id": 4, "organization": "Nova Esports Demo", "name": "Nova BGMI", "game": "BGMI",
         "competition_level": "Competitive", "budget": 500000, "required_role": "Assaulter", "member_ids": [4, 8, 12, 16, 20]},
    ]

def ensure_data():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not PLAYERS_FILE.exists():
        save_json(PLAYERS_FILE, [make_player(i) for i in range(80)])
    if not TEAMS_FILE.exists():
        save_json(TEAMS_FILE, default_teams())

def get_players() -> list[dict]:
    ensure_data()
    return load_json(PLAYERS_FILE, [])

def save_players(players: list[dict]):
    save_json(PLAYERS_FILE, players)

def get_teams() -> list[dict]:
    ensure_data()
    return load_json(TEAMS_FILE, [])

def save_teams(teams: list[dict]):
    save_json(TEAMS_FILE, teams)
