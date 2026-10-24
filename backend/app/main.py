from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import pandas as pd
import io

from .data_store import get_players, get_teams, save_teams, save_players, ensure_data
from .scoring import role_score, roster_fit, budget_score, explain
from .intelligence import router as intelligence_router

app = FastAPI(title="ScoutX AI API", version="1.0.0",
              description="Esports scouting and multi-roster intelligence prototype. Demo data is simulated.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", "http://127.0.0.1:3000",
        "http://localhost:3001", "http://127.0.0.1:3001",
    ],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

class AddMember(BaseModel):
    player_id: int

@app.on_event("startup")
def startup():
    ensure_data()

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ScoutX AI", "data_mode": "simulated_demo"}

@app.get("/api/summary")
def summary():
    players, teams = get_players(), get_teams()
    available = sum(1 for p in players if p.get("availability") == "Available")
    avg_wr = round(sum(p.get("win_rate", 0) for p in players) / max(1, len(players)), 1)
    games = sorted({p.get("game", "Unknown") for p in players})
    return {
        "total_players": len(players), "available_players": available,
        "total_teams": len(teams), "games_covered": len(games),
        "average_win_rate": avg_wr, "games": games,
        "data_mode": "SIMULATED DEMO DATA"
    }

@app.get("/api/players")
def players(game: Optional[str] = None, role: Optional[str] = None,
            search: Optional[str] = None, availability: Optional[str] = None,
            limit: int = Query(100, ge=1, le=1000)):
    rows = get_players()
    if game and game != "All Games":
        rows = [p for p in rows if p["game"] == game]
    if role and role != "All Roles":
        rows = [p for p in rows if p["role"] == role]
    if availability and availability != "All":
        rows = [p for p in rows if p["availability"] == availability]
    if search:
        q = search.lower()
        rows = [p for p in rows if q in p["name"].lower() or q in p["handle"].lower()]
    return rows[:limit]

@app.get("/api/players/{player_id}")
def player_detail(player_id: int):
    p = next((p for p in get_players() if p["id"] == player_id), None)
    if not p:
        raise HTTPException(404, "Player not found")
    return p

@app.get("/api/players/{player_id}/trend")
def player_trend(player_id: int):
    p = next((p for p in get_players() if p["id"] == player_id), None)
    if not p:
        raise HTTPException(404, "Player not found")
    return {"player_id": player_id, "trend": [
        {"match": f"Match {i+1}", "score": val} for i, val in enumerate(p.get("trend", []))
    ]}

@app.get("/api/recommendations")
def recommendations(game: str, role: str, budget: float = Query(600000, ge=0),
                    team_id: Optional[int] = None, limit: int = Query(10, ge=1, le=50)):
    all_players, teams = get_players(), get_teams()
    team = next((t for t in teams if t["id"] == team_id), None) if team_id else None
    if team_id and not team:
        raise HTTPException(404, "Team not found")
    if team and team["game"] != game:
        raise HTTPException(400, "Selected team belongs to a different game")
    member_ids = set(team.get("member_ids", [])) if team else set()
    rows = [p for p in all_players if p["game"] == game and p["role"] == role
            and p["id"] not in member_ids and p["estimated_cost"] <= budget
            and p["availability"] == "Available"]
    output = []
    for p in rows:
        rs = role_score(p["metrics"], role)
        rf = roster_fit(p["metrics"], role)
        sy = round((p["metrics"].get("coordination", 50) +
                    p["metrics"].get("team_enablement", 50) +
                    p["metrics"].get("adaptability", 50)) / 3, 2)
        bs = budget_score(p["estimated_cost"], budget)
        fit = round(0.50 * rs + 0.25 * rf + 0.15 * sy + 0.10 * bs, 2)
        output.append({**p, "role_score": rs, "roster_fit": rf, "synergy_score": sy,
                       "budget_suitability": bs, "fit_score": fit,
                       "explanation": explain(p["metrics"], role, rs, rf, p["estimated_cost"], budget)})
    output.sort(key=lambda p: p["fit_score"], reverse=True)
    return {"game": game, "role": role, "budget": budget, "team": team,
            "count": len(output), "recommendations": output[:limit],
            "formula": "fit = 0.50*role_score + 0.25*roster_fit + 0.15*synergy + 0.10*budget_suitability",
            "data_mode": "SIMULATED DEMO DATA"}

@app.get("/api/teams")
def teams():
    all_players = {p["id"]: p for p in get_players()}
    result = []
    for t in get_teams():
        members = [all_players[i] for i in t.get("member_ids", []) if i in all_players]
        result.append({**t, "members": members, "member_count": len(members),
                       "roster_status": "Needs recruitment" if len(members) < 5 else "Full roster"})
    return result

@app.get("/api/teams/{team_id}")
def team_detail(team_id: int):
    result = next((t for t in teams() if t["id"] == team_id), None)
    if not result:
        raise HTTPException(404, "Team not found")
    return result

@app.post("/api/teams/{team_id}/members")
def add_member(team_id: int, body: AddMember):
    team_rows, player_rows = get_teams(), get_players()
    team = next((t for t in team_rows if t["id"] == team_id), None)
    player = next((p for p in player_rows if p["id"] == body.player_id), None)
    if not team or not player:
        raise HTTPException(404, "Team or player not found")
    if player["game"] != team["game"]:
        raise HTTPException(400, "Player's game does not match this roster")
    if body.player_id in team["member_ids"]:
        raise HTTPException(409, "Player is already on this roster")
    team["member_ids"].append(body.player_id)
    save_teams(team_rows)
    return {"message": f"Added {player['name']} to {team['name']}", "team_id": team_id}

@app.delete("/api/teams/{team_id}/members/{player_id}")
def remove_member(team_id: int, player_id: int):
    team_rows = get_teams()
    team = next((t for t in team_rows if t["id"] == team_id), None)
    if not team:
        raise HTTPException(404, "Team not found")
    if player_id not in team["member_ids"]:
        raise HTTPException(404, "Player is not on this roster")
    team["member_ids"].remove(player_id)
    save_teams(team_rows)
    return {"message": "Player removed from roster"}

@app.post("/api/import/csv")
async def import_csv(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Upload a .csv file")
    try:
        raw = await file.read()
        df = pd.read_csv(io.BytesIO(raw))
        required = {"name", "game", "role"}
        if not required.issubset(set(df.columns)):
            raise HTTPException(400, "CSV must include at least: name, game, role")
        current = get_players()
        next_id = max([p["id"] for p in current], default=0) + 1
        imported = []
        for _, row in df.iterrows():
            metrics = {}
            for key in ["decision_making", "round_conversion", "coordination", "tactical_execution",
                        "consistency", "opening_success", "damage_impact", "trade_efficiency",
                        "survivability", "sniper_accuracy", "utility_effectiveness", "team_enablement",
                        "late_round_impact", "flank_effectiveness", "adaptability", "teamfight_impact",
                        "objective_control", "farm_efficiency"]:
                try:
                    metrics[key] = float(row[key]) if key in df.columns and pd.notna(row[key]) else 50.0
                except (TypeError, ValueError):
                    metrics[key] = 50.0
            def num(col, default):
                try: return float(row[col]) if col in df.columns and pd.notna(row[col]) else default
                except (TypeError, ValueError): return default
            p = {
                "id": next_id, "name": str(row["name"]), "handle": str(row.get("handle", f"imported_{next_id}")),
                "game": str(row["game"]), "role": str(row["role"]), "region": str(row.get("region", "Unknown")),
                "experience_years": num("experience_years", 1), "estimated_cost": num("estimated_cost", 300000),
                "availability": str(row.get("availability", "Available")), "matches_played": int(num("matches_played", 0)),
                "win_rate": num("win_rate", 50), "kd_ratio": num("kd_ratio", 1),
                "damage_per_round": num("damage_per_round", 100), "metrics": metrics,
                "trend": [50, 55, 52, 60, 58, 65], "data_source": "USER_CSV_IMPORT",
                "confidence": 0.5, "notes": "Imported from user CSV; validate source and metric scales."
            }
            imported.append(p); next_id += 1
        save_players(current + imported)
        return {"imported": len(imported), "message": "CSV imported. Imported records are not automatically verified."}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(400, f"Could not parse CSV: {exc}")


app.include_router(intelligence_router)
