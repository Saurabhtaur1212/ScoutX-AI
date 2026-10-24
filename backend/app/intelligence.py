"""ScoutX AI additional intelligence features.

These endpoints use transparent demo heuristics and simulated records. They are not trained
predictive models. Replace heuristic calculations with validated game-specific models and
licensed/verified data integrations before production use.
"""
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .data_store import get_players, get_teams

router = APIRouter(prefix="/api/intelligence", tags=["Additional intelligence"])
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FEEDBACK_FILE = DATA_DIR / "scout_feedback.json"
VIDEO_FILE = DATA_DIR / "video_evidence.json"

def _read(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def _write(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _player(pid: int):
    return next((p for p in get_players() if int(p.get("id", -1)) == pid), None)

def _metric(p: dict, key: str, fallback: float = 50.0) -> float:
    try:
        return max(0.0, min(100.0, float(p.get("metrics", {}).get(key, fallback))))
    except (TypeError, ValueError):
        return fallback

def _now():
    return datetime.now(timezone.utc).isoformat()

class VideoEvidenceIn(BaseModel):
    player_id: int
    title: str = Field(min_length=2, max_length=160)
    video_url: str = Field(min_length=8, max_length=1000)
    timestamp_seconds: int = Field(ge=0, le=86400)
    observation: str = Field(min_length=3, max_length=2000)
    tag: str = Field(default="Scouting note", max_length=80)

class FeedbackIn(BaseModel):
    player_id: int
    recommendation_id: Optional[str] = None
    useful: bool
    reason: str = Field(min_length=3, max_length=1000)
    reviewer: str = Field(default="Demo scout", max_length=120)

@router.get("/overview")
def overview():
    players, teams = get_players(), get_teams()
    feedback = _read(FEEDBACK_FILE, [])
    videos = _read(VIDEO_FILE, [])
    return {
        "features": [
            {"id":"video-evidence","name":"AI Video Evidence Finder","status":"evidence-linking MVP","description":"Attach a timestamped gameplay moment to a player and scouting observation. Automatic video understanding is not enabled."},
            {"id":"style-match","name":"Player Style Matching","status":"available","description":"Find similar tactical profiles using normalized demo metrics."},
            {"id":"meta-adaptability","name":"Meta Adaptability Tracker","status":"proxy metric","description":"Use adaptability plus the available trend series as a patch-adaptability proxy; true patch history is not yet ingested."},
            {"id":"recruitment-value","name":"Recruitment Value Estimator","status":"heuristic estimate","description":"Compare role score and estimated cost; demo prices are simulated."},
            {"id":"counterfactual","name":"Counterfactual Roster Analysis","status":"scenario comparison","description":"Compare a candidate against a roster's current average profile using heuristic role/team metrics."},
            {"id":"feedback","name":"Scout Feedback Learning Loop","status":"feedback capture","description":"Capture usefulness ratings and reasons for later offline evaluation; no automatic model retraining occurs."},
            {"id":"data-quality","name":"Data Quality Monitor","status":"available","description":"Flag missing, stale, suspicious, or low-confidence records from fields currently stored."},
            {"id":"reports","name":"Evidence-Based Scouting Reports","status":"available","description":"Generate a structured report with metrics, evidence links, limitations, and recommendation notes."}
        ],
        "counts":{"players":len(players),"teams":len(teams),"video_evidence":len(_read(VIDEO_FILE,[])),"scout_feedback":len(feedback)},
        "data_mode":"SIMULATED DEMO DATA"
    }

@router.get("/video-evidence")
def list_video_evidence(player_id: Optional[int] = None):
    rows = _read(VIDEO_FILE, [])
    if player_id is not None:
        rows = [r for r in rows if r.get("player_id") == player_id]
    return {"items": rows, "count": len(rows)}

@router.post("/video-evidence")
def add_video_evidence(body: VideoEvidenceIn):
    player = _player(body.player_id)
    if not player:
        raise HTTPException(404, "Player not found")
    rows = _read(VIDEO_FILE, [])
    item = {"id": max([r.get("id",0) for r in rows], default=0)+1,
            **body.model_dump(), "player_name": player["name"], "created_at": _now(),
            "mode":"MANUALLY LINKED EVIDENCE"}
    rows.append(item); _write(VIDEO_FILE, rows)
    return item

@router.get("/style-match/{player_id}")
def style_match(player_id: int, limit: int = 5):
    target = _player(player_id)
    if not target:
        raise HTTPException(404, "Player not found")
    keys = ["decision_making","coordination","tactical_execution","consistency","opening_success",
            "damage_impact","trade_efficiency","survivability","adaptability","team_enablement",
            "objective_control","teamfight_impact","farm_efficiency","utility_effectiveness"]
    candidates = []
    for p in get_players():
        if p["id"] == player_id or p.get("game") != target.get("game"):
            continue
        shared = [k for k in keys if k in p.get("metrics",{}) and k in target.get("metrics",{})]
        if not shared:
            continue
        distance = sum(abs(_metric(p,k)-_metric(target,k)) for k in shared) / len(shared)
        similarity = round(max(0,100-distance),1)
        candidates.append({"player":p,"similarity":similarity,
                           "shared_metrics":len(shared),
                           "explanation":f"{similarity:.1f}% metric-profile similarity across {len(shared)} shared metrics; game title matches."})
    candidates.sort(key=lambda x:x["similarity"], reverse=True)
    return {"target":target,"matches":candidates[:max(1,min(limit,20))],
            "method":"1 - mean absolute difference on shared 0-100 metrics; same-game candidates only",
            "warning":"Similarity is not proof of equivalent playstyle. Validate with match footage and coach review."}

@router.get("/meta-adaptability/{player_id}")
def meta_adaptability(player_id: int):
    p = _player(player_id)
    if not p:
        raise HTTPException(404, "Player not found")
    trend = [float(x) for x in p.get("trend",[]) if isinstance(x,(int,float))]
    trend_mean = sum(trend)/len(trend) if trend else 50.0
    trend_stability = max(0,100-(max(trend)-min(trend))) if len(trend)>1 else 50.0
    adaptability = _metric(p,"adaptability")
    proxy = round(0.65*adaptability + 0.20*trend_stability + 0.15*trend_mean,1)
    return {"player_id":player_id,"player_name":p["name"],"game":p["game"],
            "adaptability_metric":adaptability,"trend_stability_proxy":round(trend_stability,1),
            "trend_average":round(trend_mean,1),"meta_adaptability_proxy":proxy,
            "patch_history_available":False,
            "warning":"Proxy only: the current dataset has no verified patch-by-patch history. Add dated patch snapshots before treating this as a true meta-adaptability measure."}

@router.get("/recruitment-value/{player_id}")
def recruitment_value(player_id: int, budget: float = 600000):
    p = _player(player_id)
    if not p:
        raise HTTPException(404, "Player not found")
    m = p.get("metrics",{})
    role = _metric(p,"consistency")
    role_score = sum(_metric(p,k) for k in ["decision_making","damage_impact","coordination","adaptability","consistency"])/5
    cost = max(1.0,float(p.get("estimated_cost",1)))
    value = round(role_score / cost * 100000,2)
    affordability = round(max(0,min(100,100*budget/cost)),1)
    return {"player_id":player_id,"player_name":p["name"],"estimated_cost":cost,
            "budget":budget,"role_performance_proxy":round(role_score,1),
            "value_per_100k_cost":value,"budget_coverage_score":affordability,
            "within_budget":cost<=budget,"availability":p.get("availability"),
            "warning":"Cost and performance values are demo estimates, not a real market valuation or salary recommendation."}

@router.post("/counterfactual")
def counterfactual(team_id: int, candidate_id: int):
    team = next((t for t in get_teams() if t["id"] == team_id),None)
    candidate = _player(candidate_id)
    if not team or not candidate:
        raise HTTPException(404,"Team or candidate not found")
    if team["game"] != candidate["game"]:
        raise HTTPException(400,"Candidate and roster must be for the same game")
    players = {p["id"]:p for p in get_players()}
    members = [players[i] for i in team.get("member_ids",[]) if i in players]
    keys = ["coordination","team_enablement","adaptability","consistency","objective_control","teamfight_impact"]
    before = {k:round(sum(_metric(p,k) for p in members)/len(members),1) for k in keys} if members else {k:50 for k in keys}
    after_players = [p for p in members if p["id"] != candidate_id] + [candidate]
    after = {k:round(sum(_metric(p,k) for p in after_players)/len(after_players),1) for k in keys}
    deltas = {k:round(after[k]-before[k],1) for k in keys}
    return {"team":{"id":team["id"],"name":team["name"],"game":team["game"]},
            "candidate":{"id":candidate["id"],"name":candidate["name"],"role":candidate["role"]},
            "roster_size_before":len(members),"roster_size_after":len(after_players),
            "before":before,"after":after,"deltas":deltas,
            "interpretation":"Positive values indicate an increase in the roster's simple average for that metric. This is not a chemistry or match-win simulation.",
            "warning":"Counterfactual uses aggregate metrics only; it does not model map, opponent, role-slot constraints, or actual synergy."}

@router.post("/feedback")
def add_feedback(body: FeedbackIn):
    player = _player(body.player_id)
    if not player:
        raise HTTPException(404,"Player not found")
    rows = _read(FEEDBACK_FILE, [])
    item = {"id":max([r.get("id",0) for r in rows],default=0)+1,
            **body.model_dump(),"player_name":player["name"],"created_at":_now()}
    rows.append(item); _write(FEEDBACK_FILE, rows)
    return {"message":"Feedback saved for offline evaluation; no model was retrained.","item":item}

@router.get("/feedback")
def list_feedback():
    rows = _read(FEEDBACK_FILE, [])
    useful = sum(1 for r in rows if r.get("useful"))
    return {"items":rows,"count":len(rows),"useful_count":useful,
            "usefulness_rate":round(100*useful/len(rows),1) if rows else None,
            "note":"Feedback is stored for human review and offline evaluation; it does not automatically retrain a model."}

@router.get("/data-quality")
def data_quality():
    players = get_players()
    checks=[]
    for p in players:
        issues=[]
        if not p.get("name") or not p.get("game") or not p.get("role"): issues.append("Missing name, game, or role")
        if not p.get("data_source"): issues.append("Missing data source")
        if not isinstance(p.get("metrics"),dict) or not p.get("metrics"): issues.append("Missing metrics")
        else:
            invalid=[k for k,v in p["metrics"].items() if not isinstance(v,(int,float)) or v<0 or v>100]
            if invalid: issues.append("Metrics outside 0–100 or non-numeric: "+", ".join(invalid[:5]))
            if len(p["metrics"])<5: issues.append("Sparse metric profile")
        if int(p.get("matches_played",0) or 0)<10: issues.append("Low sample size (<10 matches)")
        if float(p.get("confidence",0) or 0)<0.6: issues.append("Low evidence confidence")
        if p.get("data_source") in (None,"","UNKNOWN"): issues.append("Unverified source")
        # Demo schema does not store collection timestamps or patch history, so freshness cannot be validated.
        if not p.get("last_updated"): issues.append("Freshness cannot be verified (no last_updated field)")
        checks.append({"player_id":p["id"],"name":p["name"],"game":p["game"],
                       "quality":"Needs review" if issues else "Looks complete",
                       "issue_count":len(issues),"issues":issues,
                       "data_source":p.get("data_source"),"confidence":p.get("confidence")})
    flagged=[r for r in checks if r["issues"]]
    return {"total_players":len(players),"flagged_players":len(flagged),
            "quality_rate":round(100*(len(players)-len(flagged))/max(1,len(players)),1),
            "records":checks,"common_limitations":["No source verification workflow","No last-updated timestamp in the current schema","No patch-by-patch metric snapshots"]}

@router.get("/reports/{player_id}")
def scouting_report(player_id: int):
    p = _player(player_id)
    if not p:
        raise HTTPException(404,"Player not found")
    metrics=p.get("metrics",{})
    strongest=sorted(metrics.items(),key=lambda kv:float(kv[1]) if isinstance(kv[1],(int,float)) else 0,reverse=True)[:3]
    weakest=sorted(metrics.items(),key=lambda kv:float(kv[1]) if isinstance(kv[1],(int,float)) else 100)[:3]
    videos=[v for v in _read(VIDEO_FILE,[]) if v.get("player_id")==player_id]
    return {"report_id":f"SCOUTX-{player_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "generated_at":_now(),"player":{"id":p["id"],"name":p["name"],"handle":p.get("handle"),
            "game":p["game"],"role":p["role"],"region":p.get("region"),"availability":p.get("availability")},
            "summary":f"{p['name']} is a {p['role']} candidate in {p['game']}. Review the strengths and limitations below before making a decision.",
            "strengths":[{"metric":k,"score":v} for k,v in strongest],
            "development_areas":[{"metric":k,"score":v} for k,v in weakest],
            "performance_context":{"matches_played":p.get("matches_played"),"win_rate":p.get("win_rate"),
                                  "trend":p.get("trend",[]),"confidence":p.get("confidence")},
            "evidence":videos,
            "limitations":["Demo/simulated metrics may not represent real performance.",
                           "No automated video analysis; linked clips and observations are manually supplied.",
                           "Recommendation is decision support and requires coach/scout review."]}
