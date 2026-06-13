import time
import json
from .state import AegisState

def _rule_based_response(predicted_paths, risk_score, user):
    """Generate containment actions."""
    actions = []
    actions.append(f"DISABLE_ACCOUNT: {user}")
    actions.append("REVOKE_VPN: All active sessions for this user")
    actions.append("ALERT_SOC: Level 2 security team notification")

    for path in predicted_paths[:2]:
        actions.extend(path.get("contains_actions", []))

    if risk_score >= 70:
        actions.append("ISOLATE_NETWORK: Segment affected subnet")
        actions.append("ENABLE_MFA: Force MFA reset for all users")
        actions.append("AUDIT_LOGS: Full forensic log collection")

    return {
        "response_actions": actions,
        "priority": "IMMEDIATE" if risk_score >= 70 else "HIGH",
        "estimated_containment_time": "15-30 minutes",
        "manual_steps_required": len([a for a in actions if "ALERT" in a]),
    }


async def response_node(state: AegisState) -> dict:
    """Response agent - recommends containment actions."""
    predicted_paths = state.get("predicted_paths", [])
    risk_score = state.get("risk_score", 50)
    event = state["event"]
    user = event.get("user", "unknown")
    log_entry = {"agent": "RESPONSE", "message": "Generating containment actions...", "state": "active", "timestamp": time.time()}
    result = _rule_based_response(predicted_paths, risk_score, user)
    log_entry["message"] += f"\nPriority: {result['priority']}"
    log_entry["message"] += f"\nActions: {len(result['response_actions'])} steps"
    log_entry["message"] += f"\nEst. containment: {result['estimated_containment_time']}"
    log_entry["state"] = "complete"
    return {"response_actions": result["response_actions"], "agent_log": state.get("agent_log", []) + [log_entry]}
