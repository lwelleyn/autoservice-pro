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
- **Vehicle Tracking** - Manage client vehicles with VIN, make, model, and year
- **Work Orders** - Create and track service orders with status updates
- **RESTful API** - Full CRUD operations for all entities
- **CORS Enabled** - Cross-origin resource sharing for frontend integration
- **Prometheus Metrics** - Built-in instrumentation for monitoring
- **Docker Deployment** - Containerized services with docker-compose

## Screenshots

> _Screenshots coming soon_

## Quick Start

### Prerequisites

- Docker
- Docker Compose

### Running with Docker Compose

```bash
# Clone the repository
git clone https://github.com/yourusername/AutoServicePro.git
cd AutoServicePro

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Service URLs

| Service      | URL                  |
|--------------|---------------------|
| Frontend     | http://localhost:5173 |
| Backend API  | http://localhost:8000 |
| API Docs     | http://localhost:8000/docs |
| Prometheus  | http://localhost:9090 |
| Grafana     | http://localhost:3000 |

### Stopping Services

```bash
docker-compose down
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

## DevOps Features

### Monitoring Stack

- **Prometheus** - Metrics collection and querying
- **Grafana** - Visualization dashboards
- **FastAPI Instrumentation** - Built-in request/response metrics

### CI/CD Pipeline

GitHub Actions workflow for automated:
- Code linting
- Testing
- Container building

### Containerization

- Multi-service docker-compose setup
- Health checks for dependency management
- Persistent volume for database
- Hot reload for development

## Project Structure

```
AutoServicePro/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── pages/
│   └── Dockerfile
├── docker/
│   └── ...
├── prometheus/
│   └── prometheus.yml
├── docs/
│   └── CONTEXT.md
├── docker-compose.yml
├── .github/
│   └── workflows/
└── README.md
```

## Environment Variables

### Backend

| Variable       | Default                              |
|---------------|--------------------------------------|
| DATABASE_URL  | postgresql://postgres:postgres@localhost:5432/autoservice |

### Frontend

| Variable     | Default                 |
|--------------|------------------------|
| VITE_API_URL | http://localhost:8000   |

### PostgreSQL

| Variable            | Default      |
|--------------------|-------------|
| POSTGRES_USER      | autoservice  |
| POSTGRES_PASSWORD | autoservice  |
| POSTGRES_DB        | autoservice  |

## License

MIT License