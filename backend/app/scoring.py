"""Transparent heuristic scoring for the ScoutX AI demo."""
from typing import Dict, Any

# All inputs are assumed to be normalized to 0..100.
ROLE_WEIGHTS = {
    "IGL": {
        "decision_making": 0.30,
        "round_conversion": 0.25,
        "coordination": 0.20,
        "tactical_execution": 0.15,
        "consistency": 0.10,
    },
    "Entry Fragger": {
        "opening_success": 0.30,
        "damage_impact": 0.25,
        "trade_efficiency": 0.20,
        "consistency": 0.15,
        "survivability": 0.10,
    },
    "AWPer": {
        "sniper_accuracy": 0.30,
        "opening_success": 0.25,
        "damage_impact": 0.20,
        "consistency": 0.15,
        "survivability": 0.10,
    },
    "Support": {
        "utility_effectiveness": 0.30,
        "team_enablement": 0.25,
        "coordination": 0.20,
        "consistency": 0.15,
        "survivability": 0.10,
    },
    "Lurker": {
        "late_round_impact": 0.30,
        "flank_effectiveness": 0.25,
        "survivability": 0.20,
        "consistency": 0.15,
        "damage_impact": 0.10,
    },
    "Flex": {
        "adaptability": 0.30,
        "consistency": 0.25,
        "damage_impact": 0.20,
        "coordination": 0.15,
        "survivability": 0.10,
    },
    "IGL / Captain": {
        "decision_making": 0.30,
        "teamfight_impact": 0.25,
        "coordination": 0.20,
        "objective_control": 0.15,
        "consistency": 0.10,
    },
    "Carry": {
        "damage_impact": 0.30,
        "teamfight_impact": 0.25,
        "farm_efficiency": 0.20,
        "consistency": 0.15,
        "survivability": 0.10,
    },
    "Support / Roamer": {
        "team_enablement": 0.30,
        "coordination": 0.25,
        "objective_control": 0.20,
        "consistency": 0.15,
        "survivability": 0.10,
    },
    "Assaulter": {
        "damage_impact": 0.30,
        "survivability": 0.25,
        "opening_success": 0.20,
        "consistency": 0.15,
        "adaptability": 0.10,
    },
    "Scout": {
        "decision_making": 0.25,
        "team_enablement": 0.25,
        "objective_control": 0.20,
        "consistency": 0.15,
        "adaptability": 0.15,
    },
}
DEFAULT_WEIGHTS = {
    "damage_impact": 0.25, "consistency": 0.25,
    "coordination": 0.20, "adaptability": 0.15, "survivability": 0.15,
}

def role_score(metrics: Dict[str, float], role: str) -> float:
    weights = ROLE_WEIGHTS.get(role, DEFAULT_WEIGHTS)
    total = sum(float(metrics.get(k, 50)) * w for k, w in weights.items())
    return round(max(0, min(100, total)), 2)

def roster_fit(metrics: Dict[str, float], role: str) -> float:
    """Demo proxy: combines teamwork, adaptability, and role-specific performance."""
    role_value = role_score(metrics, role)
    teamwork = (float(metrics.get("coordination", 50)) +
                float(metrics.get("team_enablement", 50)) +
                float(metrics.get("adaptability", 50))) / 3
    return round(0.65 * role_value + 0.35 * teamwork, 2)

def budget_score(cost: float, budget: float) -> float:
    if budget <= 0:
        return 100.0
    return round(max(0, min(100, 100 * (1 - cost / budget))), 2)

def explain(metrics: Dict[str, float], role: str, score: float, fit: float, cost: float, budget: float) -> list[str]:
    weights = ROLE_WEIGHTS.get(role, DEFAULT_WEIGHTS)
    ranked = sorted(weights.items(), key=lambda item: float(metrics.get(item[0], 50)), reverse=True)
    labels = {
        "decision_making": "decision-making", "round_conversion": "round conversion",
        "coordination": "team coordination", "tactical_execution": "tactical execution",
        "consistency": "consistency", "opening_success": "opening-duel success",
        "damage_impact": "damage impact", "trade_efficiency": "trade efficiency",
        "survivability": "survivability", "sniper_accuracy": "sniper accuracy",
        "utility_effectiveness": "utility effectiveness", "team_enablement": "team enablement",
        "late_round_impact": "late-round impact", "flank_effectiveness": "flank effectiveness",
        "adaptability": "adaptability", "teamfight_impact": "teamfight impact",
        "objective_control": "objective control", "farm_efficiency": "farm efficiency",
    }
    top = [labels.get(k, k.replace("_", " ")) for k, _ in ranked[:2]]
    result = [f"Role score: {score:.1f}/100 using the configured {role} metric weights.",
              f"Relative strengths: {top[0]} and {top[1]}."]
    if cost <= budget:
        result.append(f"Estimated cost fits the selected budget ({cost:,.0f} of {budget:,.0f}).")
    else:
        result.append("Estimated cost is above the selected budget.")
    result.append(f"Roster-fit heuristic: {fit:.1f}/100; validate with coach review and team scrims.")
    return result
