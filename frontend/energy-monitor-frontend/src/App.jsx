import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import StatCard from './components/StatCard';
import DeviceGrid from './components/DeviceGrid';
import Navigation from './components/Navigation';
import RealTimeAnalytics from './components/Analytics/RealTimeAnalytics';
import HistoricalData from './components/Analytics/HistoricalData';
import Schedule from './components/Analytics/Schedule';
import { devicesAPI, energyAPI } from './services/api';
import AddDeviceModal from './components/AddDeviceModal';


function App() {
  const [devices, setDevices] = useState([]);
  const [stats, setStats] = useState({
    totalPower: 0,
    todayEnergy: 0,
    todayCost: 0,
    activeDevices: 0,
    peakPower: 0,
    avgPower: 0,
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [addLoading, setAddLoading] = useState(false);


  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [devicesRes, currentRes, todayRes] = await Promise.all([
        devicesAPI.getAll(),
        energyAPI.getCurrent(),
        energyAPI.getToday(),
      ]);

      const devicesList = devicesRes.data.results;
      const currentData = currentRes.data;
      const todayData = todayRes.data;

      setDevices(devicesList);
      setStats({
        totalPower: currentData.total_power,
        todayEnergy: todayData.total_energy,
        todayCost: todayData.total_cost,
        activeDevices: currentData.devices.filter(d => d.power_state === 'on').length,
        peakPower: Math.max(...currentData.devices.map(d => d.current_power), 0),
        avgPower: currentData.total_power / currentData.devices.length,
      });
    } catch (err) {
      console.error('Ошибка загрузки данных:', err);
      setError('Ошибка подключения к серверу. Проверьте что Django запущен на http://localhost:8000');
    } finally {
      setLoading(false);
    }
  };


  const handleAddDeviceClick = () => {
    setIsAddModalOpen(true);
  };

  const handleCreateDevice = async (data) => {
    try {
      setAddLoading(true);
      setError(null);
      await devicesAPI.create(data);
      await fetchData();
      setIsAddModalOpen(false);
    } catch (err) {
      console.error('Ошибка при добавлении устройства:', err);
      setError('Ошибка при добавлении устройства');
    } finally {
      setAddLoading(false);
    }
  };


  const handleToggleDevice = async (deviceId) => {
    try {
      await devicesAPI.toggle(deviceId);
      await fetchData();
    } catch (err) {
      console.error('Ошибка при переключении устройства:', err);
      setError('Ошибка при переключении устройства');
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <Header onRefresh={fetchData} loading={loading} />

      {error && (
        <div className="error-banner">
          <div className="error-content">
            <span className="error-icon">⚠️</span>
            <span className="error-text">{error}</span>
            <button className="error-close" onClick={() => setError(null)}>✕</button>
          </div>
        </div>
      )}

      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="container">
        {activeTab === 'dashboard' && (
          <>
            <div className="stats-section">
              <h2 className="section-title">Статистика</h2>
              <div className="stats-grid">
                <StatCard
                  title="Потребление сейчас"
                  value={stats.totalPower}
                  unit="кВт"
                  icon="⚡"
                  color="#667eea"
                />
                <StatCard
                  title="За сегодня"
                  value={stats.todayEnergy}
                  unit="кВт·ч"
                  icon="📊"
                  color="#10b981"
                />
                <StatCard
                  title="Стоимость сегодня"
                  value={Math.round(stats.todayCost)}
                  unit="₽"
                  icon="💰"
                  color="#f59e0b"
                />
                <StatCard
                  title="Активные устройства"
                  value={stats.activeDevices}
                  unit={`из ${devices.length}`}
                  icon="🔌"
                  color="#ef4444"
                />
                <StatCard
                  title="Пиковое потребление"
                  value={stats.peakPower}
                  unit="кВт"
                  icon="📈"
                  color="#8b5cf6"
                />
                <StatCard
                  title="Среднее потребление"
                  value={stats.avgPower}
                  unit="кВт"
                  icon="📉"
                  color="#06b6d4"
                />
              </div>
            </div>

            <DeviceGrid
              devices={devices}
              onToggleDevice={handleToggleDevice}
              onAddDevice={handleAddDeviceClick}
              loading={loading}
            />

          </>
        )}

        {activeTab === 'analytics' && <RealTimeAnalytics />}
        {activeTab === 'history' && <HistoricalData />}
        {activeTab === 'schedule' && (
          <>
            <Schedule />
          </>
        )}
      </div>

      <footer className="footer">
        <span>
          Последнее обновление: {new Date().toLocaleTimeString('ru-RU')}
        </span>
      </footer>
      <AddDeviceModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSubmit={handleCreateDevice}
        loading={addLoading}
      />
    </div>
  );
}

export default App;
