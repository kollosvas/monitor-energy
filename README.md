# 🏠 Система мониторинга энергопотерь

Система управления умным домом с поддержкой расписания для розеток и анализом энергопотребления.  
Проект состоит из **Django backend** и **React frontend**.

Находится на стадии **разработки**

---


## 🛠️ Стек технологий

Backend:
- Django 4.2  
- Django REST Framework  
- PostgreSQL  

Frontend:
- React 18  
- Create React App  

---

## Запуск проекта

### 1. Клонирование репозитория

git clone https://github.com/kollosvas/monitor-energy.git 
cd energy_monitor

---

### 2. Backend
cd backend

#### 2.1 База данных postgreSQL
1.1. Установить с официального сайта postgreSQL 18.
1.2. Для пользователя postgres установить пароль 'admin437'.
1.3. Инициализация бд: psql -U postgres -f db_init.sql


cd backend  
python -m venv venv  
venv\Scripts\activate       (Windows)  
source venv/bin/activate    (Linux/macOS)  
pip install -r requirements.txt 

python manage.py makemigrations devices
python manage.py makemigrations energy
python manage.py migrate  

python manage.py createsuperuser

python manage.py generate_sample_data

(venv) python manage.py runserver  
→ http://localhost:8000

В новом терминале (для генерации данных):

cd backend
venv\Scripts\activate       (Windows)  
source venv/bin/activate    (Linux/macOS)  
(venv) python manage.py generate_realtime_data

---

### 3. Frontend
Скачать и установить node.js

cd ../frontend/energy-monitor-frontend
npm install -g serve

serve -s build 

→ http://localhost:3000

---

## 🌐 API и расписания

Устройства:
GET /api/devices/  
GET /api/devices/{id}/  

Расписания:
GET /api/schedules/  
POST /api/schedules/create_for_device/  
GET /api/schedules/by_device/?device_id=<id>  
PATCH /api/schedules/{id}/toggle_enabled/  
DELETE /api/schedules/{id}/  

---
### ПРИМЕРЫ РАБОТЫ:
<img width="1077" height="1793" alt="image" src="https://github.com/user-attachments/assets/e4a0300f-45a9-40db-a08e-7641eee49598" />
<img width="1075" height="1793" alt="image" src="https://github.com/user-attachments/assets/6ee20be8-dcb4-4b10-b665-ca15b73219ff" />
<img width="1074" height="1792" alt="image" src="https://github.com/user-attachments/assets/2ad3398b-8301-4604-9c14-4634172e7e48" />
<img width="1073" height="1793" alt="image" src="https://github.com/user-attachments/assets/96ca9ec3-ade9-4a03-a1a2-190d431178cd" />

---

Последнее обновление: 26 декабря 2025 года
