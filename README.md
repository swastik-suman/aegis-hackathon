# AEGIS — Autonomous Digital Immune System

> An AI security organism that continuously learns, predicts, simulates, and neutralises cyber threats before damage occurs.

**Faraway Hackathon 2026** | Team: Swastik, Rakshit, Swarnim, Ishan, Swayam

---

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
cp ../.env.example .env        # add your API key
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm start                      # runs on localhost:3000
```

---

## Architecture

| Layer | Component | Tech |
|-------|-----------|------|
| Agent orchestration | 6-node LangGraph pipeline | Python + LangGraph |
| Digital Twin | Org graph (28 nodes) | NetworkX → Sigma.js |
| Vector memory | Incident similarity recall | ChromaDB |
| Backend | WebSocket streaming server | FastAPI |
| Frontend | Command centre dashboard | React + Canvas |
| Voice | STT commands + TTS responses | Web Speech API |

### 6-Agent Pipeline
```
SENTINEL → INVESTIGATOR → THREAT INTEL → RISK AGENT → RED TEAM → RESPONSE
```

---

## Demo Events
| Button | User | Attack Type |
|--------|------|-------------|
| Event 1 | swastik.kumar | Impossible travel — Romania login at 02:17 AM |
| Event 2 | anita.sharma (CFO) | Unusual access from Singapore |
| Event 3 | john.doe (intern) | Unauthorised DB access |
| Event 4 | swarnim.patel | Large data exfiltration |

## Voice Commands
Say or click: **Blast Radius** · **Attack Paths** · **Contain Threat** · **Exec Brief**

---

## Environment Variables
```
ANTHROPIC_API_KEY=your_key_here    # optional — falls back to rule-based mode
```
