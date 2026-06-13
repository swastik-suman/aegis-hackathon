import React from 'react';

function ScoreCard({ score, containmentActive }) {
  const getColor = (s) => {
    if (s >= 85) return '#34d399';
    if (s >= 70) return '#fbbf24';
    return '#f87171';
  };

  const getStatusClass = (s) => {
    if (s >= 85) return 'status-secure';
    if (s >= 70) return 'status-warning';
    return 'status-danger';
  };

  const getLabel = (s) => {
    if (s >= 85) return 'SECURE';
    if (s >= 70) return 'AT RISK';
    return 'COMPROMISED';
  };

  const barColor = getColor(score);
  const barWidth = score + '%';

  return (
    <div className="score-card">

      {/* Primary — dominant score number */}
      <div className="score-item primary">
        <div
          className="score-value"
          style={{ color: getColor(score), transition: 'color 0.6s ease' }}
        >
          {score}
          <span style={{ fontSize: '1.2rem', fontWeight: 400, color: 'rgba(255,255,255,0.3)', marginLeft: '2px' }}>/100</span>
        </div>
        <div className="score-bar-wrap">
          <div
            className="score-bar-fill"
            style={{ width: barWidth, background: barColor }}
          />
        </div>
        <div className="score-label">Security Score</div>
      </div>

      {/* Status */}
      <div className="score-item">
        <div className={`score-value ${getStatusClass(score)}`} style={{ fontSize: '1.3rem' }}>
          {getLabel(score)}
        </div>
        <div className="score-label">Status</div>
      </div>

      {/* Containment */}
      <div className="score-item">
        <div
          className="score-value"
          style={{
            fontSize: '1.1rem',
            color: containmentActive ? '#34d399' : '#475569',
            animation: containmentActive ? 'blink 1s infinite' : 'none'
          }}
        >
          {containmentActive ? 'ACTIVE' : 'STANDBY'}
        </div>
        <div className="score-label">Containment</div>
      </div>

      {/* Agents */}
      <div className="score-item">
        <div className="score-value" style={{ fontSize: '2rem', color: '#3b82f6' }}>
          6
        </div>
        <div className="score-label">Agents Online</div>
      </div>

    </div>
  );
}

export default ScoreCard;
