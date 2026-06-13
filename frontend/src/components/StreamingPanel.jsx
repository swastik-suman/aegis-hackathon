import React, { useEffect, useRef } from 'react';

function StreamingPanel({ agentLogs }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [agentLogs]);

  return (
    <div className="streaming-panel">
      <div className="panel-header">
        \uD83E\uDD16 AEGIS Agent Stream
      </div>
      <div className="stream-content" ref={scrollRef}>
        {agentLogs.map((log, i) => (
          <div
            key={i}
            className={`stream-entry ${log.state ? log.state.toLowerCase() : ''}`}
          >
            <div className="agent-name">
              {log.agent}
            </div>
            <div className="stream-message">
              {log.message}
            </div>
          </div>
        ))}
        {agentLogs.length === 0 && (
          <div style={{ color: '#6b7280', textAlign: 'center', padding: '2rem' }}>
            \u23F3 Waiting for security events...
            <br />
            <small>Fire Event 1 to begin demo</small>
          </div>
        )}
      </div>
    </div>
  );
}

export default StreamingPanel;
