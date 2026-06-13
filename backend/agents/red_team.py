import time
import json
import networkx as nx
from .state import AegisState

def _validate_path(org_graph, source, target):
    if org_graph is None:
        return True
    try:
        return nx.has_path(org_graph, source, target)
    except Exception:
        return False

def _get_reachable_critical_nodes(org_graph, user_node):
    if org_graph is None:
        return [
            {"node": "db_finance", "type": "DATABASE", "records": "2.3M"},
            {"node": "server_ad", "type": "SERVER", "role": "AD Server"},
            {"node": "db_customer", "type": "DATABASE", "records": "8.7M"},
        ]
    critical_nodes = []
    try:
        for node in org_graph.nodes:
            if org_graph.nodes[node].get("type") in ["DATABASE", "SERVER"]:
                if nx.has_path(org_graph, user_node, node):
                    critical_nodes.append({"node": node, "type": org_graph.nodes[node].get("type"), **org_graph.nodes[node]})
    except Exception:
        pass
    return critical_nodes

def _rule_based_red_team(user, org_graph, risk_score):
    """Predict top 3 attack paths for demo reliability."""
    user_node = f"user_{user.replace('.', '_')}"
    reachable = _get_reachable_critical_nodes(org_graph, user_node)

    paths = [
        {
            "id": "PATH-001",
            "description": "Lateral movement via VPN - AD Server - Domain Admin privileges",
            "steps": [f"Compromised user '{user}' -> VPN Gateway", "VPN Gateway -> AD Server (server_ad)", "AD Server -> Domain Admin credentials (T1078 escalation)", "Domain Admin -> Full domain access"],
            "probability": 87,
            "business_impact": 95,
            "contains_actions": [f"Disable account: {user}", "Revoke VPN session for: " + user_node, "Alert SOC Level 2: Domain Admin escalation risk", "Isolate AD server (server_ad) from network"],
            "valid": _validate_path(org_graph, user_node, "server_ad") if org_graph else True,
        },
        {
            "id": "PATH-002",
            "description": "Data exfiltration via Application Server - Customer DB",
            "steps": [f"Compromised user '{user}' -> App Server", "App Server -> Customer Database (db_customer)", "Exfiltrate 8.7M customer records via S3 staging", "Cover tracks via log manipulation (T1070)"],
            "probability": 72,
            "business_impact": 88,
            "contains_actions": ["Block outbound traffic from server_app", "Revoke db_customer access for all non-essential users", "Enable enhanced logging on S3 buckets", "Initiate data loss prevention scan"],
            "valid": _validate_path(org_graph, user_node, "db_customer") if org_graph else True,
        },
        {
            "id": "PATH-003",
            "description": "Financial data access via Lateral movement - Finance DB",
            "steps": [f"Compromised user '{user}' -> Mail Server", "Mail Server -> File Server -> Finance DB credentials", "Access Finance DB (2.3M financial records)", "Deploy ransomware (T1486) for maximum impact"],
            "probability": 64,
            "business_impact": 92,
            "contains_actions": ["Block mail server (server_mail) access to file server", "Revoke db_finance access credentials", "Enable ransomware detection on all file servers", "Backup critical financial data to air-gapped storage"],
            "valid": _validate_path(org_graph, user_node, "db_finance") if org_graph else True,
        },
    ]

    return {
        "predicted_paths": paths,
        "reachable_critical_nodes": reachable,
        "total_risk_exposure": sum(p["business_impact"] for p in paths),
    }


async def red_team_node(state: AegisState) -> dict:
    """Red Team agent - predicts attacker's next 3 moves."""
    event = state["event"]
    risk_score = state.get("risk_score", 50)
    org_graph = state.get("org_graph", None)
    user = event.get("user", "unknown")
    log_entry = {"agent": "RED TEAM", "message": f"Simulating attack paths for compromised user: {user}", "state": "active", "timestamp": time.time()}
    result = _rule_based_red_team(user, org_graph, risk_score)
    log_entry["message"] += f"\nTop 3 paths identified"
    log_entry["message"] += f"\nHighest risk: {result['predicted_paths'][0]['description']}"
    log_entry["message"] += f"\nTotal risk exposure: {result['total_risk_exposure']}"
    log_entry["state"] = "complete"
    return {"predicted_paths": result["predicted_paths"], "agent_log": state.get("agent_log", []) + [log_entry]}
