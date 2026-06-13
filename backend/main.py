"""
AEGIS Backend — FastAPI + WebSocket Server
Uses AegisPipeline for all event processing.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import os
from typing import List, Dict

from agents.state import AegisState
from agents.pipeline import AegisPipeline
from agents.sentinel import _rule_based_sentinel
from memory.vector_store import add_incident_to_memory
from simulator.event_generator import get_demo_events

app = FastAPI(title="AEGIS Backend", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load org graph
import networkx as nx

def load_org_graph() -> nx.Graph:
    G = nx.Graph()
    graph_path = os.path.join(os.path.dirname(__file__), "data", "acmecorp_graph.json")
    with open(graph_path) as f:
        data = json.load(f)
    for node in data["nodes"]:
        G.add_node(node["id"], **node)
    for edge in data["edges"]:
        G.add_edge(edge["source"], edge["target"], relationship=edge["relationship"])
    return G

org_graph = load_org_graph()

# FIX #1: Use AegisPipeline as the single source of truth
pipeline = AegisPipeline(org_graph=org_graph)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_json(message)
        except Exception:
            pass

manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await handle_message(message, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# FIX #4: Fuzzy voice command matching
def fuzzy_match(command: str, keywords: list) -> str:
    """Match voice commands with fuzzy tolerance."""
    cmd = command.lower().strip()
    for keyword in keywords:
        if keyword.lower() in cmd:
            return keyword
    return ""


async def handle_message(message: dict, websocket: WebSocket):
    """Route incoming WebSocket messages to appropriate handlers."""
    action = message.get("action", "")
    if action == "fire_event":
        await handle_fire_event(message, websocket)
    elif action == "contain":
        await handle_contain(websocket)
    elif action == "voice_command":
        await handle_voice_command(message, websocket)
    elif action == "exec_brief":
        await handle_exec_brief(websocket)
    elif action == "reset_demo":
        await handle_reset_demo(websocket)


async def handle_fire_event(message: dict, websocket: WebSocket):
    """Fire a specific demo event and run through pipeline."""
    event_num = message.get("event_num", 1)
    events = get_demo_events()

    if event_num > len(events):
        await manager.send_message(websocket, {
            "type": "error",
            "message": f"Event {event_num} does not exist"
        })
        return

    event = events[event_num - 1]

    await manager.send_message(websocket, {
        "type": "event_start",
        "event": event,
        "event_num": event_num
    })

    # FIX #2: Use pipeline.run_with_callback() instead of duplicating logic
    async def ws_callback(msg_type: str, data: dict):
        data["type"] = msg_type
        await manager.send_message(websocket, data)

    result = await pipeline.run_with_callback(event, ws_callback)

    # Send affected nodes for graph highlighting
    await manager.send_message(websocket, {
        "type": "affected_nodes",
        "nodes": get_affected_nodes(event, result),
        "score": result["security_score"],
        "risk_score": result.get("risk_score", 0),
    })

    await manager.send_message(websocket, {
        "type": "pipeline_complete",
        "result": {
            "classification": result.get("anomaly_result", {}).get("classification", ""),
            "risk_score": result.get("risk_score", 0),
            "security_score": result["security_score"],
            "paths_count": len(result.get("predicted_paths", [])),
            "actions_count": len(result.get("response_actions", [])),
        }
    })


def get_affected_nodes(event: dict, state: dict) -> list:
    """Determine which graph nodes to highlight based on the event."""
    user = event.get("user", "").replace(".", "_")
    nodes = [f"user_{user}"]

    # Add nodes based on event type and details
    details = event.get("details", {})
    if details.get("location"):
        nodes.append("vpn_main")
    if details.get("device_id"):
        for n in ["device_laptop1", "device_laptop2", "device_laptop3", "device_laptop4"]:
            if n.replace("device_", "").replace("_", "-")[:3] in details.get("device_id", "").upper():
                nodes.append(n)
                break

    # Add critical targets based on event type
    if details.get("target_type") == "DATABASE":
        target = details.get("target", "")
        if target:
            nodes.append(target)
        else:
            nodes.extend(["db_finance", "db_customer"])

    if event.get("type") == "data_transfer":
        nodes.extend(["cloud_s3", "db_customer"])

    return nodes


async def handle_contain(websocket: WebSocket):
    """Execute containment actions (demo mode)."""
    await manager.send_message(websocket, {
        "type": "containment_start",
        "message": "Executing containment actions..."
    })

    actions = [
        "Disabling compromised account...",
        "Revoking VPN session...",
        "Alerting SOC Level 2...",
        "Isolating affected network segment...",
        "Enforcing MFA reset...",
        "Initiating forensic log collection...",
    ]

    for action in actions:
        await manager.send_message(websocket, {
            "type": "containment_step",
            "message": action
        })
        await asyncio.sleep(0.8)

    await manager.send_message(websocket, {
        "type": "containment_complete",
        "message": "Containment actions executed successfully.",
        "security_score": 88
    })

    # Record incident in memory for learning
    add_incident_to_memory({
        "trigger_event": "swastik.kumar login from Romania",
        "mitre_technique": "T1078",
        "attack_chain": "Phishing - Credential Compromise - Lateral Movement",
        "risk_score": 71,
        "response_taken": "Account disabled, VPN revoked, SOC alerted"
    })


async def handle_voice_command(message: dict, websocket: WebSocket):
    """Handle voice commands with fuzzy matching."""
    command = message.get("command", "").lower()

    # FIX #4: Fuzzy matching instead of exact string match
    matched = fuzzy_match(command, ["blast radius", "attack path", "contain threat", "executive brief"])

    if "blast radius" in matched or "blast" in command:
        await manager.send_message(websocket, {
            "type": "voice_response",
            "command": command,
            "message": "3 critical servers reachable. Finance DB holds 2.3M records. Immediate action: revoke VPN for swastik.kumar.",
            "affected_nodes": ["server_app", "server_ad", "db_finance", "db_customer"],
            "blast_radius": {
                "users_affected": 8,
                "databases_at_risk": 3,
                "servers_at_risk": 4,
                "total_records": "11M+"
            }
        })
    elif "attack path" in matched or "path" in command:
        await manager.send_message(websocket, {
            "type": "voice_response",
            "command": command,
            "message": "Top attack path: VPN to AD Server to Domain Admin privileges. 87% probability. Immediate action: isolate AD server.",
            "affected_nodes": ["vpn_main", "server_ad"],
        })
    elif "contain" in matched or "contain" in command:
        await handle_contain(websocket)
    elif "brief" in matched or "brief" in command:
        await handle_exec_brief(websocket)
    else:
        await manager.send_message(websocket, {
            "type": "voice_response",
            "command": command,
            "message": "Command not recognized. Try: blast radius, attack path, contain threat, or executive brief.",
        })


async def handle_exec_brief(websocket: WebSocket):
    """Generate executive brief."""
    await manager.send_message(websocket, {
        "type": "exec_brief",
        "title": "AEGIS Security Incident Report",
        "timestamp": "2026-06-14T15:00:00Z",
        "summary": "Credential compromise via phishing detected for user swastik.kumar",
        "affected_systems": ["VPN Gateway", "AD Server", "Finance DB", "Customer DB"],
        "mitre_techniques": ["T1078 - Valid Accounts", "T1566 - Phishing"],
        "risk_level": "CRITICAL (71/100)",
        "timeline": [
            {"time": "02:17 AM", "event": "Unusual login from Romania"},
            {"time": "02:18 AM", "event": "Device fingerprint mismatch detected"},
            {"time": "02:23 AM", "event": "Unauthorized database access attempt"},
            {"time": "02:31 AM", "event": "Large data transfer detected"},
            {"time": "02:35 AM", "event": "Containment actions executed"},
        ],
        "actions_taken": [
            "Account disabled",
            "VPN session revoked",
            "SOC Level 2 alerted",
            "Network segment isolated",
            "MFA enforcement activated",
        ],
        "recommendations": [
            "Implement conditional access policies",
            "Deploy advanced threat detection on VPN gateways",
            "Review all privileged account access",
            "Conduct phishing awareness training",
        ]
    })


async def handle_reset_demo(websocket: WebSocket):
    """Reset demo state."""
    await manager.send_message(websocket, {
        "type": "demo_reset",
        "message": "Demo environment reset",
        "security_score": 94
    })


@app.get("/api/graph")
async def get_graph():
    """Return org graph for frontend visualization."""
    data = {
        "nodes": [{"id": n, **org_graph.nodes[n]} for n in org_graph.nodes],
        "edges": [{"source": u, "target": v, **org_graph[u][v]} for u, v in org_graph.edges],
    }
    return data


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "agents": 6, "graph_nodes": len(org_graph.nodes)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
