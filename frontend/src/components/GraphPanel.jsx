import React, { useEffect, useRef, useState } from 'react';

const NODE_COLORS = {
  USER: '#3b82f6',
  DEVICE: '#10b981',
  SERVER: '#8b5cf6',
  VPN_GATEWAY: '#f59e0b',
  DATABASE: '#ef4444',
  CLOUD_RESOURCE: '#06b6d4',
};

function GraphPanel({ graphData, activeNodes, activeEdges, teamMode }) {
  const canvasRef = useRef(null);
  const [positions, setPositions] = useState({});
  const animationRef = useRef(null);
  const [hoveredNode, setHoveredNode] = useState(null);

  // Initialize positions using simple force layout
  useEffect(() => {
    if (!graphData.nodes.length) return;
    const nodes = graphData.nodes;
    const edges = graphData.edges;
    const newPositions = {};
    
    // Place nodes in a circle
    const centerX = 400;
    const centerY = 250;
    const radius = 200;
    
    nodes.forEach((node, i) => {
      const angle = (2 * Math.PI * i) / nodes.length;
      newPositions[node.id] = {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
        vx: 0,
        vy: 0,
      };
    });
    
    // Simple force-directed layout
    for (let iter = 0; iter < 200; iter++) {
      const forces = {};
      nodes.forEach(n => {
        forces[n.id] = { fx: 0, fy: 0 };
      });
      
      // Repulsion between all nodes
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const ni = nodes[i].id;
          const nj = nodes[j].id;
          const dx = newPositions[nj].x - newPositions[ni].x;
          const dy = newPositions[nj].y - newPositions[ni].y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = 5000 / (dist * dist);
          forces[ni].fx -= (dx / dist) * force;
          forces[ni].fy -= (dy / dist) * force;
          forces[nj].fx += (dx / dist) * force;
          forces[nj].fy += (dy / dist) * force;
        }
      }
      
      // Attraction along edges
      edges.forEach(e => {
        if (newPositions[e.source] && newPositions[e.target]) {
          const dx = newPositions[e.target].x - newPositions[e.source].x;
          const dy = newPositions[e.target].y - newPositions[e.source].y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = (dist - 80) * 0.01;
          forces[e.source].fx += (dx / dist) * force;
          forces[e.source].fy += (dy / dist) * force;
          forces[e.target].fx -= (dx / dist) * force;
          forces[e.target].fy -= (dy / dist) * force;
        }
      });
      
      // Center gravity
      nodes.forEach(n => {
        const dx = centerX - newPositions[n.id].x;
        const dy = centerY - newPositions[n.id].y;
        forces[n.id].fx += dx * 0.005;
        forces[n.id].fy += dy * 0.005;
      });
      
      // Apply forces
      nodes.forEach(n => {
        const id = n.id;
        newPositions[id].x += forces[id].fx * 0.5;
        newPositions[id].y += forces[id].fy * 0.5;
      });
    }
    
    setPositions(newPositions);
  }, [graphData]);

  // Draw graph
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || Object.keys(positions).length === 0) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    function draw() {
      ctx.clearRect(0, 0, width, height);
      
      // Draw edges
      graphData.edges.forEach(edge => {
        const pos1 = positions[edge.source];
        const pos2 = positions[edge.target];
        if (!pos1 || !pos2) return;
        
        const isActive = activeEdges.includes(edge.source) || activeEdges.includes(edge.target) ||
                        activeEdges.includes(edge.source + '-' + edge.target) ||
                        teamMode === 'red';
        
        ctx.beginPath();
        ctx.moveTo(pos1.x, pos1.y);
        ctx.lineTo(pos2.x, pos2.y);
        ctx.strokeStyle = isActive ? '#f59e0b' : 'rgba(75, 85, 99, 0.3)';
        ctx.lineWidth = isActive ? 2 : 1;
        if (isActive) {
          ctx.shadowColor = '#f59e0b';
          ctx.shadowBlur = 8;
        }
        ctx.stroke();
        ctx.shadowBlur = 0;
      });
      
      // Draw nodes
      graphData.nodes.forEach(node => {
        const pos = positions[node.id];
        if (!pos) return;
        
        const isActive = activeNodes.includes(node.id);
        const isHovered = hoveredNode === node.id;
        const baseColor = NODE_COLORS[node.type] || '#9ca3af';
        
        // Node glow for active
        if (isActive) {
          ctx.beginPath();
          ctx.arc(pos.x, pos.y, 20, 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(239, 68, 68, 0.2)';
          ctx.fill();
        }
        
        // Node circle
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, isHovered ? 14 : 10, 0, Math.PI * 2);
        ctx.fillStyle = isActive ? '#ef4444' : baseColor;
        ctx.fill();
        
        // Node border
        ctx.strokeStyle = isActive ? '#fff' : 'rgba(255,255,255,0.3)';
        ctx.lineWidth = isActive ? 2 : 1;
        ctx.stroke();
        
        // Label
        ctx.fillStyle = isActive ? '#fff' : 'rgba(255,255,255,0.7)';
        ctx.font = isHovered ? 'bold 10px sans-serif' : '9px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(node.label, pos.x, pos.y + (isHovered ? 24 : 20));
        
        // Pulse animation for active nodes
        if (isActive) {
          const time = Date.now() / 1000;
          const pulseRadius = 10 + Math.sin(time * 3) * 5;
          ctx.beginPath();
          ctx.arc(pos.x, pos.y, pulseRadius, 0, Math.PI * 2);
          ctx.strokeStyle = `rgba(239, 68, 68, ${0.5 + Math.sin(time * 3) * 0.3})`;
          ctx.lineWidth = 2;
          ctx.stroke();
        }
      });
      
      animationRef.current = requestAnimationFrame(draw);
    }
    
    draw();
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [graphData, positions, activeNodes, activeEdges, teamMode, hoveredNode]);

  // Handle mouse interactions
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    canvas.onmousemove = (e) => {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      let found = null;
      graphData.nodes.forEach(node => {
        const pos = positions[node.id];
        if (!pos) return;
        const dx = x - pos.x;
        const dy = y - pos.y;
        if (dx * dx + dy * dy < 225) { // 15px radius
          found = node.id;
        }
      });
      setHoveredNode(found);
      canvas.style.cursor = found ? 'pointer' : 'default';
    };
  }, [graphData, positions]);

  return (
    <div className="graph-panel">
      <canvas
        ref={canvasRef}
        width={800}
        height={500}
        className="graph-container"
      />
      <div className="graph-legend">
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <div key={type} className="legend-item">
            <div className="legend-dot" style={{ background: color }} />
            {type.replace('_', ' ')}
          </div>
        ))}
      </div>
    </div>
  );
}

export default GraphPanel;
