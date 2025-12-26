import React, { useState } from 'react';

function DeviceCard({ device, onToggle, loading }) {
  const [toggling, setToggling] = useState(false);

  const handleToggle = async () => {
    setToggling(true);
    await onToggle(device.id);
    setToggling(false);
  };

  const isOnline = device.status === 'online';
  const isOn = device.power_state === 'on';
  const powerPercent = (device.current_power / device.rated_power) * 100;

  return (
    <div className={`device-card ${!isOnline ? 'offline' : ''}`}>
      <div className="device-header">
        <h3 className="device-name">{device.name}</h3>
        <span className={`device-badge ${isOnline ? 'online' : 'offline'}`}>
          {isOnline ? '🟢 Online' : '🔴 Offline'}
        </span>
      </div>

      <div className="device-type">{device.device_type}</div>

      <div className="device-status-info">
        <span className={`power-status ${isOn ? 'on' : 'off'}`}>
          {isOn ? '✅ Включен' : '❌ Выключен'}
        </span>
      </div>

      <div className="device-power-display">
        <div className="power-value">
          <span className="current-power">{device.current_power.toFixed(2)}</span>
          <span className="power-unit">кВт</span>
        </div>
        <div className="power-info">
          из {device.rated_power} кВт
        </div>
      </div>

      <div className="power-bar-container">
        <div className="power-bar">
          <div 
            className="power-bar-fill"
            style={{
              width: `${Math.min(powerPercent, 100)}%`,
              backgroundColor: powerPercent > 80 ? '#ef4444' : powerPercent > 50 ? '#f59e0b' : '#10b981'
            }}
          ></div>
        </div>
        <div className="power-percent">{Math.round(powerPercent)}%</div>
      </div>

      <div className="device-details">
        <div className="detail-item">
          <span className="detail-label">Последнее обновление:</span>
          <span className="detail-value">
            {new Date(device.last_update).toLocaleTimeString('ru-RU')}
          </span>
        </div>
      </div>

      <button
        className={`btn-toggle ${isOn ? 'btn-off' : 'btn-on'}`}
        onClick={handleToggle}
        disabled={toggling || !isOnline}
        title={!isOnline ? 'Устройство оффлайн' : ''}
      >
        {toggling ? '⏳' : isOn ? '⏹ Выключить' : '▶ Включить'}
      </button>
    </div>
  );
}

export default DeviceCard;
