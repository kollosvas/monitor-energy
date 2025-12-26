import React from 'react';

function StatCard({ title, value, unit, icon, color }) {
  return (
    <div className="stat-card" style={{ borderLeft: `4px solid ${color}` }}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-content">
        <div className="stat-title">{title}</div>
        <div className="stat-value" style={{ color }}>
          {typeof value === 'number' ? value.toFixed(2) : value}
        </div>
        <div className="stat-unit">{unit}</div>
      </div>
    </div>
  );
}

export default StatCard;
