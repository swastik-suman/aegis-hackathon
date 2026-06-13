from typing import TypedDict, Optional

class AegisState(TypedDict, total=False):
    # Input event from simulator
    event: dict
    # Sentinel output
    anomaly_result: dict  # {classification: str, anomalies: list[str], details: str}
    # Investigator output
    attack_chain: str
    mitre_technique: str  # e.g. "T1078"
    investigator_log: str
    # Threat Intel output
    threat_intel: dict  # {actor: str, ttps: list, campaigns: list}
    # Risk Agent output
    risk_score: int  # 0-100
    # Red Team output
    predicted_paths: list  # [{description, probability, impact, actions}]
    # Response Agent output
    response_actions: list[str]
    # Memory
    similar_incidents: list  # [{id, summary, response_taken}]
    # Agent log for streaming
    agent_log: list  # [{agent: str, message: str, state: str}]
    # Security score
    security_score: int  # 0-100, starts at 94
    # Demo mode flag
    demo_mode: bool
