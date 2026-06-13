import time
import json
import networkx as nx
from .state import AegisState

def _rule_based_risk(event: dict, mitre_technique: str, org_graph: nx.Graph) -> dict:
    """Calculate business impact score 0-100."""
    base_score = 30
    technique_severity = {"T1078": 25, "T1566": 20, "T1486": 30, "T1048": 25, "T1059": 20}
    base_score += technique_severity.get(mitre_technique, 15)

    target_type = event.get("details", {}).get("target_type", "USER")
    type_multiplier = {"DATABASE": 1.4, "SERVER": 1.3, "CLOUD_RESOURCE": 1.2, "VPN_GATEWAY": 1.15, "DEVICE": 1.0, "USER": 0.85}
    base_score *= type_multiplier.get(target_type, 1.0)

    if org_graph:
        user = event.get("user", "").replace(".", "_")
        user_node = f"user_{user}"
        try:
            critical_nodes = [n for n in org_graph.nodes if org_graph.nodes[n].get("type") in ["DATABASE", "SERVER"]]
            reachable = sum(1 for cn in critical_nodes if nx.has_path(org_graph, user_node, cn))
            base_score += min(reachable * 3, 20)
        except Exception:
            pass

    final_score = min(int(base_score), 100)
    return {
        "risk_score": final_score,
        "factors": [f"Base event score: 30", f"MITRE {mitre_technique}: +{technique_severity.get(mitre_technique, 15)}", f"Target type ({target_type}): x{type_multiplier.get(target_type, 1.0)}"],
    }


async def risk_agent_node(state: AegisState) -> dict:
    """Risk Agent - calculates business impact score."""
    event = state["event"]
    mitre_technique = state.get("mitre_technique", "")
    org_graph = state.get("org_graph", None)
    log_entry = {"agent": "RISK AGENT", "message": "Calculating business impact...", "state": "active", "timestamp": time.time()}
    result = _rule_based_risk(event, mitre_technique, org_graph)
    log_entry["message"] += f"\nRisk Score: {result['risk_score']}/100"
    log_entry["state"] = "complete"
    return {"risk_score": result["risk_score"], "agent_log": state.get("agent_log", []) + [log_entry]}
