"""
AEGIS Pipeline — LangGraph 6-agent orchestration.
Used directly by main.py WebSocket handlers.
"""
import networkx as nx
from typing import Any
from .state import AegisState
from .sentinel import sentinel_node
from .investigator import investigator_node
from .threat_intel import threat_intel_node
from .risk_agent import risk_agent_node
from .red_team import red_team_node
from .response import response_node


class AegisPipeline:
    """Main pipeline that routes events through all 6 agents."""
    
    def __init__(self, org_graph: nx.Graph = None):
        self.org_graph = org_graph
        self.nodes = [
            ("SENTINEL", sentinel_node),
            ("INVESTIGATOR", investigator_node),
            ("THREAT INTEL", threat_intel_node),
            ("RISK AGENT", risk_agent_node),
            ("RED TEAM", red_team_node),
            ("RESPONSE", response_node),
        ]

    async def run(self, event: dict) -> AegisState:
        """Run a single event through the full 6-agent pipeline."""
        state: AegisState = {
            "event": event,
            "org_graph": self.org_graph,
            "agent_log": [],
            "similar_incidents": [],
            "predicted_paths": [],
            "response_actions": [],
            "security_score": 94,
            "demo_mode": True,
        }

        for name, func in self.nodes:
            result = await func(state)
            state.update(result)

        # Calculate final security score
        risk = state.get("risk_score", 0)
        state["security_score"] = max(0, 94 - risk)
        return state

    async def run_with_callback(self, event: dict, callback) -> AegisState:
        """Run pipeline with streaming callback for WebSocket updates."""
        state: AegisState = {
            "event": event,
            "org_graph": self.org_graph,
            "agent_log": [],
            "similar_incidents": [],
            "predicted_paths": [],
            "response_actions": [],
            "security_score": 94,
            "demo_mode": True,
        }

        for name, func in self.nodes:
            await callback("node_start", {"node": name})
            result = await func(state)
            state.update(result)

            # Stream logs for this agent
            for log_entry in state.get("agent_log", []):
                if log_entry.get("agent") == name:
                    await callback("agent_update", {
                        "agent": log_entry.get("agent", ""),
                        "state": log_entry.get("state", "active"),
                        "message": log_entry.get("message", ""),
                        "streaming": True,
                    })

        risk = state.get("risk_score", 0)
        state["security_score"] = max(0, 94 - risk)
        await callback("score_update", {"score": state["security_score"]})
        return state
