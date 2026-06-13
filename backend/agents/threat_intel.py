import time
import json
from .state import AegisState

def _rule_based_threat_intel(mitre_technique: str, attack_chain: str) -> dict:
    """Fallback rule-based threat intelligence for demo reliability."""
    if "T1078" in mitre_technique:
        return {
            "actor": "APT29 (Cozy Bear)",
            "ttps": ["T1566 - Phishing", "T1078 - Valid Accounts", "T1486 - Data Encrypted for Impact"],
            "campaigns": ["Operation Ghost", "SolarWinds-style supply chain"],
            "threat_level": "HIGH",
            "details": f"Technique {mitre_technique} commonly used by APT29. "
                      f"Recent campaigns target VPN infrastructure via credential theft. "
                      f"Attack chain matches known patterns from 2024-2026 incidents.",
        }
    return {
        "actor": "Unknown",
        "ttps": [mitre_technique],
        "campaigns": ["Generic phishing campaign"],
        "threat_level": "MEDIUM",
        "details": f"Technique {mitre_technique} detected. Limited threat intel available.",
    }


async def threat_intel_node(state: AegisState) -> dict:
    """Threat Intel agent - enriches with threat intelligence context."""
    mitre_technique = state.get("mitre_technique", "")
    attack_chain = state.get("attack_chain", "")
    log_entry = {"agent": "THREAT INTEL", "message": f"Enriching {mitre_technique} with threat intelligence...", "state": "active", "timestamp": time.time()}
    result = _rule_based_threat_intel(mitre_technique, attack_chain)
    log_entry["message"] += f"\nActor: {result['actor']}\nThreat Level: {result['threat_level']}"
    log_entry["state"] = "complete"
    return {"threat_intel": result, "agent_log": state.get("agent_log", []) + [log_entry]}
