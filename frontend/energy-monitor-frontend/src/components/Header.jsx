import React from 'react';

function Header({ onRefresh, loading }) {
  return (
    <div className="header">
      <div className="header-content">
        <h1 className="header-title">
          Energy loss monitoring system
        </h1>
        <p className="header-subtitle">
          Система мониторинга энергопотерь
        </p>
      </div>
      <button
        className={`btn-refresh ${loading ? 'loading' : ''}`}
        onClick={onRefresh}
        disabled={loading}
        title="Обновить данные"
      >
        {loading ? '⏳' : '🔄'} Обновить
      </button>
    </div>
  );
}

export default Header;
