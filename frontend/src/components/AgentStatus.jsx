import React from 'react';

const AGENTS = [
  { name: 'SENTINEL',    icon: '🔍' },
  { name: 'INVESTIGATOR',icon: '🕵️' },
  { name: 'THREAT INTEL',icon: '🧠' },
  { name: 'RISK AGENT',  icon: '📊' },
  { name: 'RED TEAM',    icon: '🔴' },
  { name: 'RESPONSE',    icon: '🛡️' }
];

function AgentStatus({ logs }) {
  const getAgentState = (agentName) => {
    const agentLogs = logs.filter(l => l.agent === agentName);
    if (agentLogs.length === 0) return 'idle';
    return agentLogs[agentLogs.length - 1].state;
  };

  return (
    <div className="agent-status-bar">
      {AGENTS.map(agent => {
        const state = getAgentState(agent.name);
        return (
          <div key={agent.name} className={`agent-indicator ${state}`}>
            <div className={`indicator-dot ${state}`} />
            <div className="agent-label">{agent.icon} {agent.name}</div>
            <div className="agent-state">{state.toUpperCase()}</div>
          </div>
        );
      })}
    </div>
  );
}

export default AgentStatus;
