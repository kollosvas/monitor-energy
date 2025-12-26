import React, { useState } from 'react';
import { energyAPI } from '../../services/api';
import { exportToCSV, exportToJSON } from '../../utils/exportUtils';
import { getMonthName } from '../../utils/dateUtils';

function HistoricalData() {
  const [selectedPeriod, setSelectedPeriod] = useState('month');
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth());
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchHistoricalData = async () => {
    try {
      setLoading(true);

      let response;
      if (selectedPeriod === 'month') {
        response = await energyAPI.getDaily(selectedYear, selectedMonth + 1);
      } else if (selectedPeriod === 'year') {
        response = await energyAPI.getMonthly(selectedYear);
      }

      setData(response.data || []);
    } catch (error) {
      console.error('Ошибка загрузки данных:', error);
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (format) => {
    if (format === 'csv') {
      exportToCSV(data, `energy_${selectedYear}_${selectedMonth + 1}.csv`);
    } else if (format === 'json') {
      exportToJSON(data, `energy_${selectedYear}_${selectedMonth + 1}.json`);
    }
  };

  return (
    <div className="historical-section">
      <h2>Исторические данные</h2>

      <div className="filter-controls">
        <div className="filter-group">
          <label>Период:</label>
          <select value={selectedPeriod} onChange={(e) => setSelectedPeriod(e.target.value)}>
            <option value="month">По дням</option>
            <option value="year">По месяцам</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Год:</label>
          <select value={selectedYear} onChange={(e) => setSelectedYear(parseInt(e.target.value))}>
            {[2023, 2024, 2025].map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>

        {selectedPeriod === 'month' && (
          <div className="filter-group">
            <label>Месяц:</label>
            <select value={selectedMonth} onChange={(e) => setSelectedMonth(parseInt(e.target.value))}>
              {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].map(month => (
                <option key={month} value={month}>{getMonthName(month)}</option>
              ))}
            </select>
          </div>
        )}

        <button className="btn-primary" onClick={fetchHistoricalData} disabled={loading}>
          {loading ? '⏳ Загрузка...' : '🔍 Поиск'}
        </button>
      </div>

      <div className="export-controls">
        <button className="btn-export" onClick={() => handleExport('csv')}>
          📥 Экспорт CSV
        </button>
        <button className="btn-export" onClick={() => handleExport('json')}>
          📥 Экспорт JSON
        </button>
      </div>

      {data.length > 0 && (
        <div className="data-table">
          <table>
            <thead>
              <tr>
                <th>Дата</th>
                <th>Потребление (кВт·ч)</th>
                <th>Средняя мощность (кВт)</th>
                <th>Пиковая мощность (кВт)</th>
                <th>Стоимость (₽)</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row, idx) => (
                <tr key={idx}>
                  <td>{row.date || row.month || 'N/A'}</td>
                  <td>{parseFloat(row.total_energy || 0).toFixed(2)}</td>
                  <td>{parseFloat(row.avg_power || 0).toFixed(2)}</td>
                  <td>{parseFloat(row.peak_power || 0).toFixed(2)}</td>
                  <td>{parseFloat(row.cost || 0).toFixed(0)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && data.length === 0 && (
        <div className="empty-state">
          <p>Нет данных для выбранного периода</p>
        </div>
      )}
    </div>
  );
}

export default HistoricalData;