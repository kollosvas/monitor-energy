import React from 'react';
import DeviceCard from './DeviceCard';

function DeviceGrid({ devices, onToggleDevice, onAddDevice, loading }) {
  if (!devices || devices.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📱</div>
        <h2>Нет устройств</h2>
        <p>Добавьте первое устройство для начала мониторинга</p>

        <button className="add-device-button" onClick={onAddDevice}>
          + Добавить устройство
        </button>
      </div>
    );
  }

  return (
    <div className="devices-section">
      <h2 className="section-title">Устройства</h2>
      <div className="devices-grid">
        {devices.map((device) => (
          <DeviceCard
            key={device.id}
            device={device}
            onToggle={onToggleDevice}
            loading={loading}
          />
        ))}

        {/* Последняя карточка с плюсом */}
        <button
          type="button"
          className="device-card add-device-card"
          onClick={onAddDevice}
        >
          <div className="add-device-inner">
            <span className="add-device-plus">+</span>
            <span className="add-device-text">Добавить устройство</span>
          </div>
        </button>
      </div>
    </div>
  );
}

export default DeviceGrid;
