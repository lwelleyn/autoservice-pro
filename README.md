# AutoService Pro

A modern full-stack car service management application built with FastAPI, React, and PostgreSQL. Manage clients, vehicles, and work orders efficiently with a complete CRUD interface.

## Tech Stack

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)

## Architecture

```
                          ┌─────────────────────┐
                          │   Frontend (React)   │
                          │      :5173           │
                          └──────────┬──────────┘
                                     │
                          ┌──────────▼──────────┐
                          │  Backend (FastAPI) │
                          │      :8000         │
                          └──────────┬──────────┘
                                     │
                 ┌───────────────────┼───────────────────┐
                 │                   │                   │
        ┌────────▼────────┐  ┌─────────▼────────┐  ┌────────▼────────┐
        │   PostgreSQL  │  │   Prometheus    │  │    Grafana     │
        │     :5432    │  │     :9090      │  │     :3000      │
        └─────────────┘  └────────────────┘  └────────────────┘
```

## Features

- **Client Management** - Add, view, update, and delete client records
- **Vehicle Tracking** - Manage client vehicles with VIN, brand, model, and year
- **Work Orders** - Create and track service orders with status updates
- **RESTful API** - Full CRUD operations for all entities, with input validation
- **Cascade Delete** - Deleting a client removes their cars and work orders
- **Database Migrations** - Schema managed by Alembic, applied on container start
- **CORS Enabled** - Allowed origins configured through an environment variable
- **Prometheus Metrics** - Built-in instrumentation and a provisioned Grafana dashboard
- **Docker Deployment** - Containerized services with docker-compose

## Screenshots

### Clients Management
![Clients](docs/screenshots/clients.png)

### Cars Management
![Cars](docs/screenshots/cars.png)

### Work Orders
![Work Orders](docs/screenshots/work-orders.png)

### API Documentation
![API Docs](docs/screenshots/api-docs-1.png)

## Quick Start

### Prerequisites

- Docker
- Docker Compose (v2, the `docker compose` command)

### Running with Docker Compose

```bash
# Clone the repository
git clone https://github.com/lwelleyn/autoservice-pro.git
cd autoservice-pro

# Create your local settings (passwords live here, the file is not committed)
cp .env.example .env

# Start all services
docker compose up --build -d

# View logs
docker compose logs -f
```

Database migrations are applied automatically when the backend container starts.

### Service URLs

| Service      | URL                           | Notes |
|--------------|-------------------------------|-------|
| Frontend     | http://localhost:5173         | |
| Backend API  | http://localhost:8000         | |
| API Docs     | http://localhost:8000/docs    | Swagger UI |
| Health check | http://localhost:8000/health  | Also checks the database connection |
| Metrics      | http://localhost:8000/metrics | Prometheus format |
| Prometheus   | http://localhost:9090         | |
| Grafana      | http://localhost:3000         | Login from `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD` |

PostgreSQL is not published to the host by default. To reach it from your machine
(psql, running the backend outside Docker), uncomment the `ports` block of the `db`
service in `docker-compose.yml`.

### Stopping Services

```bash
docker compose down
```

## API Endpoints

### Clients

| Method | Endpoint       | Description         |
|--------|---------------|-------------------|
| GET    | /clients      | List all clients   |
| GET    | /clients/{id} | Get client by ID |
| POST   | /clients     | Create new client |
| PUT    | /clients/{id} | Update client    |
| DELETE | /clients/{id} | Delete client    |

### Cars

| Method | Endpoint   | Description       |
|--------|-----------|-----------------|
| GET    | /cars     | List all cars    |
| GET    | /cars/{id} | Get car by ID    |
| POST   | /cars     | Create new car   |
| PUT    | /cars/{id} | Update car      |
| DELETE | /cars/{id} | Delete car      |

### Work Orders

| Method | Endpoint          | Description            |
|--------|------------------|----------------------|
| GET    | /work-orders     | List all work orders  |
| GET    | /work-orders/{id}| Get work order by ID |
| POST   | /work-orders    | Create work order    |
| PUT    | /work-orders/{id}| Update work order   |
| DELETE | /work-orders/{id}| Delete work order  |

### Data model and validation

| Entity     | Fields | Rules |
|------------|--------|-------|
| Client     | `name`, `phone`, `email` | name up to 100 chars, phone up to 20, valid email up to 100 |
| Car        | `client_id`, `brand`, `model`, `year`, `vin` | brand/model up to 50 chars; year from 1900 to next year; VIN is exactly 17 letters/digits without I, O, Q and must be unique |
| Work order | `car_id`, `description`, `status` | description up to 500 chars; status is `pending`, `in_progress`, `completed` or `cancelled` |

List endpoints return flat objects. `GET /clients/{id}` also returns the client's cars
with their work orders, and `GET /cars/{id}` returns the car's work orders.

| Status | Meaning |
|--------|---------|
| 404    | The object, or the client/car it refers to, does not exist |
| 409    | A car with this VIN already exists |
| 422    | Validation failed (`detail` is a list of problems) |

Deleting a client also deletes their cars and work orders; deleting a car deletes its work orders.

## DevOps Features

### Monitoring Stack

- **Prometheus** - Scrapes the backend `/metrics` endpoint
- **Grafana** - Prometheus datasource and the "AutoService Pro — Backend" dashboard
  (RPS, latency percentiles, errors) are provisioned from `grafana/`
- **FastAPI Instrumentation** - Built-in request/response metrics

### CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`), runs on pushes to `main` and on pull requests:
- Backend: ruff, pytest, Alembic migrations against PostgreSQL, Docker image build
- Frontend: ESLint, production build, Docker image build

### Containerization

- Multi-service docker-compose setup configured through `.env`
- Health checks for the database and the backend
- Persistent volume for database
- Hot reload for development

## Development

### Backend tests and linter

Tests use an in-memory SQLite database, so no running PostgreSQL is needed.

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt

pytest          # tests
ruff check .    # linter
```

### Database migrations

The schema is managed by Alembic (`backend/alembic/`). Inside Docker, migrations run on
every backend start. To work with them manually:

```bash
# Apply all migrations
docker compose exec backend alembic upgrade head

# Create a migration after changing app/models.py
docker compose exec backend alembic revision --autogenerate -m "describe the change"

# Roll back the last migration
docker compose exec backend alembic downgrade -1
```

A database created by an older version of the app (before Alembic) is adopted
automatically: existing tables are kept and only the missing changes are applied.

### Frontend linter and build

```bash
cd frontend
npm ci
npm run lint
npm run build
```

## Project Structure

```
autoservice-pro/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application, CORS, metrics, /health
│   │   ├── config.py        # Settings from environment variables
│   │   ├── database.py      # Engine, session, Base
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas and validation
│   │   └── routers/         # clients.py, cars.py, work_orders.py
│   ├── alembic/             # Database migrations
│   ├── tests/               # pytest tests
│   ├── alembic.ini
│   ├── pyproject.toml       # ruff and pytest configuration
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── App.css
│   │   ├── api.js           # API client
│   │   ├── main.jsx
│   │   └── pages/           # ClientsPage, CarsPage, WorkOrdersPage
│   └── Dockerfile
├── grafana/
│   ├── provisioning/        # Datasource and dashboard provider
│   └── dashboards/          # Dashboard JSON
├── prometheus/
│   └── prometheus.yml
├── docs/
│   ├── CONTEXT.md
│   └── screenshots/
├── .github/
│   └── workflows/ci.yml
├── docker-compose.yml
├── .env.example
└── README.md
```

## Environment Variables

With Docker Compose all variables are set in `.env` (template: `.env.example`).

| Variable               | Used by            | Example / default | Description |
|------------------------|--------------------|-------------------|-------------|
| POSTGRES_USER          | db, backend        | `autoservice` | Database user |
| POSTGRES_PASSWORD      | db, backend        | required | Database password |
| POSTGRES_DB            | db, backend        | `autoservice` | Database name |
| CORS_ORIGINS           | backend            | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated origins allowed to call the API |
| VITE_API_URL           | frontend           | `http://localhost:8000` | Backend address as seen from the browser |
| GRAFANA_ADMIN_USER     | grafana            | `admin` | Grafana admin login |
| GRAFANA_ADMIN_PASSWORD | grafana            | required | Grafana admin password |

Docker Compose builds the backend's `DATABASE_URL` from the `POSTGRES_*` values. When the
backend runs outside Docker it reads `DATABASE_URL` directly
(default: `postgresql://postgres:postgres@localhost:5432/autoservice`) and `CORS_ORIGINS`.

## License

MIT License
