import React from 'react';

function ExecBrief({ data }) {
  if (!data) return null;

  const handleDownload = () => {
    const content = `AEGIS SECURITY INCIDENT REPORT
Generated: ${data.timestamp}

SUMMARY
${data.summary}

AFFECTED SYSTEMS
${data.affected_systems.join('\n')}

MITRE ATT&CK TECHNIQUES
${data.mitre_techniques.join('\n')}

RISK LEVEL
${data.risk_level}

TIMELINE
${data.timeline.map(t => `${t.time} - ${t.event}`).join('\n')}

ACTIONS TAKEN
${data.actions_taken.join('\n')}

RECOMMENDATIONS
${data.recommendations.map(r => `- ${r}`).join('\n')}`.trim();

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'aegis-incident-report.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="exec-brief">
      <div className="brief-header">
        <h3 className="brief-title">📋 {data.title || 'AEGIS Security Incident Report'}</h3>
        <button className="btn-demo" onClick={handleDownload} style={{ fontSize: '0.78rem', padding: '0.4rem 0.9rem' }}>
          ⬇ Download Report
        </button>
      </div>

      <div className="brief-body">

        <div className="brief-section full-width">
          <h4>Summary</h4>
          <p>{data.summary}</p>
        </div>

        <div className="brief-section">
          <h4>Affected Systems</h4>
          <ul>
            {data.affected_systems.map((sys, i) => <li key={i}>{sys}</li>)}
          </ul>
        </div>

        <div className="brief-section">
          <h4>MITRE ATT&CK Techniques</h4>
          <ul>
            {data.mitre_techniques.map((tech, i) => <li key={i}>{tech}</li>)}
          </ul>
        </div>

        <div className="brief-section">
          <h4>Risk Level</h4>
          <p className="risk-critical">{data.risk_level}</p>
        </div>

        <div className="brief-section">
          <h4>Actions Taken</h4>
          <ul>
            {data.actions_taken.map((a, i) => <li key={i}>{a}</li>)}
          </ul>
        </div>

        <div className="brief-section full-width">
          <h4>Timeline</h4>
          <ul>
            {data.timeline.map((t, i) => (
              <li key={i}><strong>{t.time}</strong> — {t.event}</li>
            ))}
          </ul>
        </div>

        <div className="brief-section full-width">
          <h4>Recommendations</h4>
          <ul>
            {data.recommendations.map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </div>

      </div>
    </div>
  );
}

export default ExecBrief;
