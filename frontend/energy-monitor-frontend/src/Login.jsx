import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css'; // Импорт стилей

const Login = () => {
  const navigate = useNavigate();
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    setError('');
    
    // Простая валидация
    if (!login || !password) {
      setError('Пожалуйста, заполните все поля');
      return;
    }
    
    // Здесь должна быть ваша логика авторизации (API запрос)
    // Пример для демонстрации:
    if (login === 'admin' && password === '123') {
      localStorage.setItem('token', 'your-token');
      localStorage.setItem('user', login);
      navigate('/');
    } else {
      setError('Неверный логин или пароль');
    }
  };

  const handleRecovery = () => {
    // Логика восстановления пароля
    alert('Функция восстановления пароля будет доступна позже');
    // Или navigate('/recovery');
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h2 className="login-title">
            Вход в ELMS
          </h2>
          <p className="login-subtitle">
            Введите свои учетные данные
          </p>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin}>
          <div className="form-group-login">
            <label className="form-label">
              Логин
            </label>
            <input
              type="text"
              className="form-input"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              placeholder="Введите ваш логин"
            />
          </div>

          <div className="password-group">
            <label className="form-label">
              Пароль
            </label>
            <input
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Введите ваш пароль"
            />
          </div>

          <button
            type="submit"
            className="btn-login"
          >
            Войти
          </button>

          <button
            type="button"
            className="btn-recovery"
            onClick={handleRecovery}
          >
            Восстановить пароль
          </button>
        </form>

        <div className="login-footer">
          © 2026 ELM system
        </div>
      </div>
    </div>
  );
};

export default Login;