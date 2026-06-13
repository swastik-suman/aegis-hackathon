import React, { useState, useEffect, useRef, useCallback } from 'react';
import GraphPanel from './components/GraphPanel';
import StreamingPanel from './components/StreamingPanel';
import ScoreCard from './components/ScoreCard';
import AgentStatus from './components/AgentStatus';
import VoiceInterface from './components/VoiceInterface';
import ExecBrief from './components/ExecBrief';
import './App.css';

const WS_URL = 'ws://localhost:8000/ws';

function App() {
  const [securityScore, setSecurityScore] = useState(94);
  const [agentLogs, setAgentLogs] = useState([]);
  const [activeNodes, setActiveNodes] = useState([]);
  const [activeEdges, setActiveEdges] = useState([]);
  const [teamMode, setTeamMode] = useState('blue');
  const [execBriefData, setExecBriefData] = useState(null);
  const [voiceResponse, setVoiceResponse] = useState('');
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [containmentActive, setContainmentActive] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);

  const wsRef = useRef(null);

  useEffect(() => {
    connectWebSocket();
    fetchGraphData();
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const connectWebSocket = () => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;
    ws.onopen = () => setWsConnected(true);
    ws.onclose = () => {
      setWsConnected(false);
      setTimeout(connectWebSocket, 3000);
    };
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWsMessage(data);
    };
  };

  const speak = (text) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleWsMessage = useCallback((data) => {
    switch (data.type) {
      case 'event_start':
        setAgentLogs(prev => [...prev, {
          agent: 'SYSTEM',
          message: `Firing event ${data.event_num}: ${data.event.user} from ${data.event.details?.location || 'unknown'} (${data.event.timestamp || 'unknown time'})`,
          state: 'active',
          timestamp: Date.now()
        }]);
        break;

      case 'node_start':
        setAgentLogs(prev => [...prev, {
          agent: data.node,
          message: 'Initializing...',
          state: 'active',
          timestamp: Date.now()
        }]);
        break;

      case 'agent_update':
        setAgentLogs(prev => [...prev, {
          agent: data.agent,
          message: data.message,
          state: data.state,
          timestamp: Date.now(),
          streaming: data.streaming
        }]);
        break;

      case 'score_update':
        setSecurityScore(data.score);
        break;

      case 'affected_nodes':
        setActiveNodes(data.nodes || []);
        break;

      case 'containment_start':
        setContainmentActive(true);
        speak('Executing containment protocol. Isolating compromised systems.');
        setAgentLogs(prev => [...prev, {
          agent: 'RESPONSE',
          message: data.message,
          state: 'active',
          timestamp: Date.now()
        }]);
        break;

      case 'containment_step':
        setAgentLogs(prev => [...prev, {
          agent: 'RESPONSE',
          message: data.message,
          state: 'active',
          timestamp: Date.now()
        }]);
        break;

      case 'containment_complete':
        setContainmentActive(false);
        setSecurityScore(data.security_score);
        setActiveNodes([]);
        setActiveEdges([]);
        speak('Containment complete. Security score restored to ' + data.security_score + ' out of 100.');
        setAgentLogs(prev => [...prev, {
          agent: 'RESPONSE',
          message: data.message,
          state: 'complete',
          timestamp: Date.now()
        }]);
        break;

      case 'voice_response':
        setVoiceResponse(data.message);
        speak(data.message);
        if (data.affected_nodes) setActiveNodes(data.affected_nodes);
        break;

      case 'exec_brief':
        setExecBriefData(data);
        speak('Executive brief generated. Incident report is ready for review.');
        break;

      case 'demo_reset':
        setSecurityScore(94);
        setAgentLogs([]);
        setActiveNodes([]);
        setActiveEdges([]);
        setExecBriefData(null);
        setVoiceResponse('');
        setContainmentActive(false);
        break;

      case 'pipeline_complete':
        setAgentLogs(prev => [...prev, {
          agent: 'SYSTEM',
          message: `Pipeline complete. Score: ${data.result?.security_score}/100 | Risk: ${data.result?.risk_score}/100 | ${data.result?.paths_count || 0} attack paths | ${data.result?.actions_count || 0} containment actions`,
          state: 'complete',
          timestamp: Date.now()
        }]);
        break;

      default:
        break;
    }
  }, []);

  const fetchGraphData = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/graph');
      const data = await res.json();
      setGraphData(data);
    } catch (err) {
      setGraphData(getFallbackGraph());
    }
  };

  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  const fireEvent = (eventNum) => sendMessage({ action: 'fire_event', event_num: eventNum });
  const triggerContainment = () => sendMessage({ action: 'contain' });
  const triggerVoiceCommand = (command) => sendMessage({ action: 'voice_command', command });
  const triggerExecBrief = () => sendMessage({ action: 'exec_brief' });
  const resetDemo = () => sendMessage({ action: 'reset_demo' });

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <h1 className="title">AEGIS</h1>
          <p className="tagline">Autonomous Digital Immune System</p>
        </div>
        <div className="header-controls">
          <button
            className={`team-toggle ${teamMode === 'red' ? 'red-mode' : 'blue-mode'}`}
            onClick={() => setTeamMode(prev => prev === 'red' ? 'blue' : 'red')}
          >
            {teamMode === 'red' ? '🔴 RED TEAM' : '🔵 BLUE TEAM'}
          </button>
          <span className={`connection-status ${wsConnected ? 'connected' : 'disconnected'}`}>
            {wsConnected ? '● CONNECTED' : '● CONNECTING...'}
          </span>
        </div>
      </header>

      <div className="dashboard">
        <ScoreCard score={securityScore} containmentActive={containmentActive} />

        <div className="main-content">
          <GraphPanel
            graphData={graphData}
            activeNodes={activeNodes}
            activeEdges={activeEdges}
            teamMode={teamMode}
          />
          <StreamingPanel agentLogs={agentLogs} />
        </div>

        <AgentStatus logs={agentLogs} teamMode={teamMode} />

        <div className="demo-controls">
          <button onClick={() => fireEvent(1)} className="btn-demo">
            🎯 Event 1: Romania Login
          </button>
          <button onClick={() => fireEvent(2)} className="btn-demo">
            🔁 Event 2: CFO Access
          </button>
          <button onClick={() => fireEvent(3)} className="btn-demo">
            ⚠️ Event 3: DB Breach
          </button>
          <button onClick={() => fireEvent(4)} className="btn-demo">
            📤 Event 4: Data Exfil
          </button>
          <span className="controls-divider" aria-hidden="true"></span>
          <button onClick={triggerContainment} className="btn-contain" disabled={containmentActive}>
            🛡️ Execute Containment
          </button>
          <button onClick={triggerExecBrief} className="btn-exec-brief">
            📋 Executive Brief
          </button>
          <button onClick={resetDemo} className="btn-reset">
            🔄 Reset Demo
          </button>
        </div>

        <VoiceInterface onCommand={triggerVoiceCommand} voiceResponse={voiceResponse} />
        {execBriefData && <ExecBrief data={execBriefData} />}
      </div>
    </div>
  );
}

function getFallbackGraph() {
  return {
    nodes: [
      { id: 'user_swastik', label: 'swastik.kumar', type: 'USER', department: 'engineering' },
      { id: 'user_cfo', label: 'anita.sharma', type: 'USER', department: 'finance' },
      { id: 'user_intern', label: 'john.doe', type: 'USER', department: 'marketing' },
      { id: 'user_hr', label: 'michael.ross', type: 'USER', department: 'hr' },
      { id: 'vpn_main', label: 'VPN-GATEWAY-01', type: 'VPN_GATEWAY', department: 'IT' },
      { id: 'server_app', label: 'APP-SERVER-01', type: 'SERVER', department: 'engineering' },
      { id: 'server_ad', label: 'AD-SERVER-01', type: 'SERVER', department: 'IT' },
      { id: 'server_mail', label: 'MAIL-SERVER-01', type: 'SERVER', department: 'IT' },
      { id: 'server_file', label: 'FILE-SERVER-01', type: 'SERVER', department: 'IT' },
      { id: 'db_finance', label: 'FINANCE-DB', type: 'DATABASE', department: 'finance', records: '2.3M' },
      { id: 'db_customer', label: 'CUSTOMER-DB', type: 'DATABASE', department: 'sales', records: '8.7M' },
      { id: 'db_hr', label: 'HR-DB', type: 'DATABASE', department: 'hr', records: '45K' },
      { id: 'db_logs', label: 'INTERNAL-LOGS', type: 'DATABASE', department: 'IT' },
      { id: 'cloud_s3', label: 'S3-BACKUP-BUCKET', type: 'CLOUD_RESOURCE', department: 'IT' },
      { id: 'cloud_lambda', label: 'LAMBDA-AUTH', type: 'CLOUD_RESOURCE', department: 'engineering' },
      { id: 'cloud_rds', label: 'RDS-PROD', type: 'CLOUD_RESOURCE', department: 'engineering' },
    ],
    edges: [
      { source: 'user_swastik', target: 'vpn_main', relationship: 'connects_to' },
      { source: 'user_swastik', target: 'server_app', relationship: 'can_access' },
      { source: 'user_cfo', target: 'vpn_main', relationship: 'connects_to' },
      { source: 'user_cfo', target: 'db_finance', relationship: 'has_permission' },
      { source: 'vpn_main', target: 'server_app', relationship: 'connects_to' },
      { source: 'vpn_main', target: 'server_ad', relationship: 'connects_to' },
      { source: 'vpn_main', target: 'db_customer', relationship: 'connects_to' },
      { source: 'server_app', target: 'db_customer', relationship: 'can_access' },
      { source: 'server_app', target: 'db_finance', relationship: 'can_access' },
      { source: 'server_ad', target: 'server_app', relationship: 'can_access' },
      { source: 'server_ad', target: 'db_logs', relationship: 'can_access' },
      { source: 'server_file', target: 'db_logs', relationship: 'can_access' },
      { source: 'server_file', target: 'cloud_s3', relationship: 'connects_to' },
      { source: 'db_finance', target: 'db_customer', relationship: 'can_access' },
    ],
  };
}

export default App;
