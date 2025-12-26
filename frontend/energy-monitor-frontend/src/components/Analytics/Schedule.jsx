import React, { useState } from 'react';
import styles from './Schedule.module.css';

const Schedule = () => {
  const [devices, setDevices] = useState([
    {
      id: 1,
      name: 'Кондиционер',
      type: 'climate',
      status: 'on',
      schedules: [
        { id: 1, time: '09:00', action: 'on', enabled: true },
        { id: 2, time: '18:00', action: 'off', enabled: true },
      ],
    },
    {
      id: 2,
      name: 'Освещение',
      type: 'light',
      status: 'on',
      schedules: [
        { id: 3, time: '07:00', action: 'on', enabled: true },
        { id: 4, time: '22:00', action: 'off', enabled: true },
      ],
    },
    {
      id: 3,
      name: 'Холодильник',
      type: 'appliance',
      status: 'on',
      schedules: [],
    },
  ]);

  const [newSchedule, setNewSchedule] = useState({ deviceId: '', time: '', action: 'off' });
  const [expandedDevice, setExpandedDevice] = useState(null);

  // Добавить расписание для устройства
  const addSchedule = (deviceId) => {
    if (!newSchedule.time) {
      alert('Введи время!');
      return;
    }

    setDevices(
      devices.map((device) => {
        if (device.id === deviceId) {
          return {
            ...device,
            schedules: [
              ...device.schedules,
              {
                id: Date.now(),
                time: newSchedule.time,
                action: newSchedule.action,
                enabled: true,
              },
            ],
          };
        }
        return device;
      })
    );

    setNewSchedule({ deviceId: '', time: '', action: 'off' });
  };

  // Удалить расписание
  const removeSchedule = (deviceId, scheduleId) => {
    setDevices(
      devices.map((device) => {
        if (device.id === deviceId) {
          return {
            ...device,
            schedules: device.schedules.filter((s) => s.id !== scheduleId),
          };
        }
        return device;
      })
    );
  };

  // Переключить расписание (вкл/выкл)
  const toggleSchedule = (deviceId, scheduleId) => {
    setDevices(
      devices.map((device) => {
        if (device.id === deviceId) {
          return {
            ...device,
            schedules: device.schedules.map((s) =>
              s.id === scheduleId ? { ...s, enabled: !s.enabled } : s
            ),
          };
        }
        return device;
      })
    );
  };

  // Переключить устройство (вкл/выкл)
  const toggleDevice = (deviceId) => {
    setDevices(
      devices.map((device) =>
        device.id === deviceId
          ? { ...device, status: device.status === 'on' ? 'off' : 'on' }
          : device
      )
    );
  };

  const getDeviceIcon = (type) => {
    switch (type) {
      case 'climate':
        return '❄️';
      case 'light':
        return '💡';
      case 'appliance':
        return '🧊';
      default:
        return '⚡';
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>📅 Расписание розеток</h2>
        <p className={styles.subtitle}>Настрой автоматическое включение/отключение устройств</p>
      </div>

      <div className={styles.devicesList}>
        {devices.map((device) => (
          <div key={device.id} className={styles.deviceCard}>
            {/* Заголовок устройства */}
            <div className={styles.deviceHeader}>
              <div className={styles.deviceInfo}>
                <span className={styles.deviceIcon}>{getDeviceIcon(device.type)}</span>
                <div className={styles.deviceName}>
                  <h3>{device.name}</h3>
                  <span className={`${styles.status} ${styles[`status-${device.status}`]}`}>
                    {device.status === 'on' ? '🟢 Включено' : '🔴 Отключено'}
                  </span>
                </div>
              </div>

              <div className={styles.deviceActions}>
                <button
                  className={`${styles.toggleBtn} ${styles[`toggle-${device.status}`]}`}
                  onClick={() => toggleDevice(device.id)}
                >
                  {device.status === 'on' ? 'Отключить' : 'Включить'}
                </button>
                <button
                  className={styles.expandBtn}
                  onClick={() => setExpandedDevice(expandedDevice === device.id ? null : device.id)}
                >
                  {expandedDevice === device.id ? '▼' : '▶'}
                </button>
              </div>
            </div>

            {/* Расписания и форма добавления */}
            {expandedDevice === device.id && (
              <div className={styles.deviceExpanded}>
                {/* Существующие расписания */}
                <div className={styles.schedulesList}>
                  <h4>Текущее расписание:</h4>
                  {device.schedules.length > 0 ? (
                    <div className={styles.scheduleItems}>
                      {device.schedules.map((schedule) => (
                        <div key={schedule.id} className={styles.scheduleItem}>
                          <input
                            type="checkbox"
                            checked={schedule.enabled}
                            onChange={() => toggleSchedule(device.id, schedule.id)}
                            className={styles.checkbox}
                          />
                          <div className={styles.scheduleInfo}>
                            <span className={styles.time}>🕐 {schedule.time}</span>
                            <span className={`${styles.action} ${styles[`action-${schedule.action}`]}`}>
                              {schedule.action === 'on' ? '✅ Включить' : '❌ Отключить'}
                            </span>
                          </div>
                          <button
                            className={styles.deleteBtn}
                            onClick={() => removeSchedule(device.id, schedule.id)}
                          >
                            🗑️ Удалить
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className={styles.noSchedule}>Расписание не установлено</p>
                  )}
                </div>

                {/* Форма добавления нового расписания */}
                <div className={styles.addScheduleForm}>
                  <h4>Добавить расписание:</h4>
                  <div className={styles.formRow}>
                    <div className={styles.formGroup}>
                      <label>Время:</label>
                      <input
                        type="time"
                        value={newSchedule.deviceId === device.id ? newSchedule.time : ''}
                        onChange={(e) =>
                          setNewSchedule({
                            ...newSchedule,
                            deviceId: device.id,
                            time: e.target.value,
                          })
                        }
                        className={styles.timeInput}
                      />
                    </div>

                    <div className={styles.formGroup}>
                      <label>Действие:</label>
                      <select
                        value={newSchedule.deviceId === device.id ? newSchedule.action : 'off'}
                        onChange={(e) =>
                          setNewSchedule({
                            ...newSchedule,
                            deviceId: device.id,
                            action: e.target.value,
                          })
                        }
                        className={styles.actionSelect}
                      >
                        <option value="on">✅ Включить</option>
                        <option value="off">❌ Отключить</option>
                      </select>
                    </div>

                    <button
                      className={styles.addBtn}
                      onClick={() => addSchedule(device.id)}
                    >
                      ➕ Добавить
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Общая статистика */}
      <div className={styles.stats}>
        <div className={styles.statCard}>
          <h4>Всего устройств</h4>
          <p className={styles.statValue}>{devices.length}</p>
        </div>
        <div className={styles.statCard}>
          <h4>Включено</h4>
          <p className={styles.statValue}>{devices.filter((d) => d.status === 'on').length}</p>
        </div>
        <div className={styles.statCard}>
          <h4>Расписаний установлено</h4>
          <p className={styles.statValue}>
            {devices.reduce((sum, d) => sum + d.schedules.length, 0)}
          </p>
        </div>
        <div className={styles.statCard}>
          <h4>Активных расписаний</h4>
          <p className={styles.statValue}>
            {devices.reduce((sum, d) => sum + d.schedules.filter((s) => s.enabled).length, 0)}
          </p>
        </div>
      </div>
    </div>
  );
};

export default Schedule;