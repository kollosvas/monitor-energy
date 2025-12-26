import React from 'react';
import DeviceCard from './DeviceCard';

function DeviceGrid({ devices, onToggleDevice, loading }) {
  if (devices.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📱</div>
        <h2>Нет устройств</h2>
        <p>Добавьте первое устройство для начала мониторинга</p>
      </div>
    );
  }

  return (
    <div className="devices-section">
      <h2 className="section-title">Устройства</h2>
      <div className="devices-grid">
        {devices.map(device => (
          <DeviceCard
            key={device.id}
            device={device}
            onToggle={onToggleDevice}
            loading={loading}
          />
        ))}
      </div>
    </div>
  );
}

export default DeviceGrid;
