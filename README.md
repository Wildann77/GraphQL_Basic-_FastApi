# GraphQL Basic - FastAPI

This is a modern, high-performance GraphQL API built with **FastAPI** and **Strawberry**, designed to be scalable and easy to maintain. It includes a complete Dockerized environment with MySQL, Redis, and Monitoring.

## 🚀 Features

- **GraphQL API**: Built with [Strawberry](https://strawberry.rocks/) and [FastAPI](https://fastapi.tiangolo.com/).
- **Asynchronous Database**: High-performance async MySQL access using [SQLAlchemy 2.0](https://www.sqlalchemy.org/) and `aiomysql`.
- **Dockerized**: specific `Dockerfile` with multi-stage builds (Builder, Base, Development, Production) and `docker-compose` setup.
- **Hot Reload**: Supports `docker compose watch` for seamless development.
- **Rate Limiting**: Integrated Redis-based rate limiting using [SlowAPI](https://github.com/laurentS/slowapi).
- **Migrations**: Database schema management with [Alembic](https://alembic.sqlalchemy.org/).
- **Monitoring**: Prometheus metrics integration.
- **Structured Logging**: JSON logging using `structlog`.


## 🛠 Tech Stack

- **Language**: Python 3.11
- **Web Framework**: FastAPI
- **GraphQL**: Strawberry
- **Database**: MySQL 8.0
- **Cache**: Redis 7
- **ORM**: SQLAlchemy (Async)
- **Containerization**: Docker & Docker Compose

## ⚡ Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose (v2.22+ recommended for `watch` mode).
- [Make](https://www.gnu.org/software/make/) (Optional, triggers commands easily).

### 1. Configuration

Create a `.env` file in the root directory. You can copy the example below:

```ini
# App
APP_NAME="GraphQL API"
ENVIRONMENT=development
DEBUG=true
APP_PORT=8000

# Database
# Format: mysql+aiomysql://<user>:<password>@<host>:<port>/<db_name>
DATABASE_URL=mysql+aiomysql://user:password@db:3306/graphql_db
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=graphql_db
MYSQL_USER=user
MYSQL_PASSWORD=password
MYSQL_PORT=3306

# Security
SECRET_KEY=change_this_to_a_secure_random_string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis & Rate Limiting
REDIS_URL=redis://redis:6379/0
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=console
```

### 2. Running with Docker (Recommended)

Start the application in **Watch Mode** (changes in `src/` will define immediate updates):

```bash
make watch
# Or directly: docker compose up --watch
```

Start in standard detached mode:
```bash
make up
```

Stop the application:
```bash
make down
```

### 3. Local Development (Optional)

If you prefer running Python locally:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
make dev-install
# Or: pip install -r requirements.txt && pip install -r requirements-dev.txt
```

## 📚 API Documentation

Once the app is running (default port 8000), accessing the following endpoints:

- **GraphQL Playground**: [http://localhost:8000/graphql](http://localhost:8000/graphql)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Adminer (Database GUI)**: [http://localhost:8080](http://localhost:8080)
  - **System**: MySQL
  - **Server**: `db`
  - **Username/Password**: Matches your `.env` (e.g., `user`/`password`)

## 🗄 Database Migrations

This project uses Alembic for database migrations.

**Create a new migration:**
```bash
make migrate m="create users table"
```

**Apply migrations to DB:**
```bash
make migrate-up
```

**Undo last migration:**
```bash
make migrate-down
```

## 🧪 Testing & Linting

Run the test suite:
```bash
make test
```

Run code formatting and linting:
```bash
make format
make lint
```

## 📂 Project Structure

```
├── alembic/            # Database migrations
├──src/
│   ├── core/           # Core config (DB, Security, Logging)
│   ├── features/       # Feature modules (Business Logic)
│   ├── main.py         # App entry point
│   └── config.py       # Pydantic settings
├── tests/              # Pytest suite
├── Dockerfile          # Multi-stage Docker build
├── docker-compose.yml  # Services orchestration
└── Makefile            # Command shortcuts
```
