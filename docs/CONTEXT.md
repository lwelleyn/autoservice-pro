# AutoService Pro

## Stack
- Backend: Python + FastAPI + SQLAlchemy + Alembic
- Frontend: React + Vite
- DB: PostgreSQL (Docker)
- DevOps: Docker Compose, GitHub Actions, Prometheus + Grafana

## Что уже сделано
- [x] FastAPI с CORS (origins из переменной окружения `CORS_ORIGINS`)
- [x] React фронтенд: страницы клиентов, машин и заказ-нарядов
- [x] docker-compose.yml (5 сервисов: backend, frontend, db, prometheus, grafana), настройки в `.env`
- [x] БД модели: Client, Car, WorkOrder с каскадным удалением
- [x] CRUD API эндпоинты для всех моделей
- [x] Валидация входных данных (VIN, год, длины полей, статус заказа), 409 на дубликат VIN
- [x] Бэкенд разбит на модули (`backend/app/`: config, database, models, schemas, routers)
- [x] Миграции Alembic, применяются при старте контейнера
- [x] Тесты бэкенда (pytest, SQLite in-memory) и линтер ruff
- [x] GitHub Actions CI: ruff, pytest, миграции на PostgreSQL, ESLint, сборка фронтенда и Docker-образов
- [x] Prometheus + Grafana: datasource и дашборд (RPS, задержка, ошибки) через provisioning
- [x] Healthcheck бэкенда (`/health`)
- [x] Фронтенд: общий API-клиент (`src/api.js`), показ реальных ошибок бэкенда

## Следующий шаг
- [ ] Аутентификация и роли (сейчас API открыт всем)
- [ ] Пагинация, поиск и фильтры в списковых эндпоинтах
- [ ] Тесты фронтенда (Vitest + React Testing Library)
- [ ] Production-сборка фронтенда (nginx вместо dev-сервера Vite) и отдельный compose-файл для продакшена
- [ ] CD: публикация Docker-образов и деплой
- [ ] Алерты в Prometheus/Grafana (доля 5xx, задержка)
- [ ] Обновить скриншоты в README под текущий интерфейс и API
