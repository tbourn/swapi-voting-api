# ⚡ SWAPI Voting API

> Production-ready FastAPI microservice for importing, storing, and serving Star Wars data from SWAPI with async support, SQL database storage, rate limiting, and interactive API docs.

---

## 📚 Table of Contents

- [⚡ SWAPI Voting API](#-swapi-voting-api)
  - [📚 Table of Contents](#-table-of-contents)
  - [📄 Description](#-description)
  - [✅ Features](#-features)
  - [🔒 Security and Compliance](#-security-and-compliance)
  - [⚙️ Installation](#️-installation)
    - [Windows](#windows)
    - [macOS / Linux](#macos--linux)
  - [⚡ Environment Configuration](#-environment-configuration)
  - [🐳 Running with Docker](#-running-with-docker)
  - [🌐 API Endpoints](#-api-endpoints)
    - [🟠 Import Endpoints](#-import-endpoints)
    - [🟠 Characters](#-characters)
    - [🟠 Films](#-films)
    - [🟠 Starships](#-starships)
    - [📜 Documentation](#-documentation)
  - [👨‍💻 Author \& Maintainer](#-author--maintainer)

---

## 📄 Description

The **SWAPI Voting API** is a modern, production-ready RESTful microservice built with FastAPI. It integrates with the public Star Wars API (SWAPI) to fetch, store, and serve Star Wars characters, films, starships, and other entities with rich validation, search, and pagination.

Ideal for building frontend integrations, fan projects, or learning best practices for professional Python APIs.

---

## ✅ Features

- 🌌 Import Star Wars data directly from the public SWAPI.
- 🗄️ SQL-backed relational database with robust data models.
- 🔎 Paginated listing and search endpoints.
- ⚡ Fully async implementation with FastAPI.
- 📜 Automatic Swagger UI documentation.
- 🔐 Secure environment-based configuration with rate limiting support.

---

## 🔒 Security and Compliance

- 🛡️ CORS policy for frontend apps.
- ✅ Graceful error handling with consistent JSON responses.
- 🔐 Environment variable configuration for production secrets.
- 📈 Redis-based IP rate limiting.

---

## ⚙️ Installation

### Windows

```powershell
# Clone repository
git clone https://github.com/tbourn/swapi-voting-api.git
cd swapi-voting-api

# Create and activate virtual environment
py -3.12 -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations (if using Alembic)
alembic upgrade head

# Start the FastAPI server
uvicorn src.main:app --reload
```

### macOS / Linux
```bash
# Clone repository
git clone https://github.com/tbourn/swapi-voting-api.git
cd swapi-voting-api

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations (if using Alembic)
alembic upgrade head

# Start the FastAPI server
uvicorn src.main:app --reload
```

⚠️ Make sure Python 3.12 or higher is installed. If python3.12 is not available on PATH, install it first, or use the correct alias (like python3 if it points to 3.12+).

## ⚡ Environment Configuration

```shell
# =============================================================================
# SWAPI Voting API — Example Environment Variables
# =============================================================================

# Database
DATABASE_URL=sqlite+aiosqlite:///./app.db

# SWAPI Voting API settings
APP_NAME='SWAPI Voting API'
APP_VERSION=1.0.0
DEFAULT_PAGE_SIZE=20

# External APIs
SWAPI_BASE_URL=https://swapi.info/api
VERIFY_SWAPI_SSL=True

# Rate Limiting
UPSTASH_REDIS_URL=rediss://YOUR_UPSTASH_REDIS_URL
```

✅ Replace YOUR_UPSTASH_REDIS_URL with your actual Upstash Redis connection string. 
⚠️ Do not commit real secrets to version control. 

## 🐳 Running with Docker
This repository includes a production-ready Dockerfile.

Build the image:
```shell
docker build -t swapi-voting-api .
```

Run the container:
```shell
docker run --env-file .env -p 8000:8000 swapi-voting-api
```

✅ Your FastAPI server will be available at:
```shell
[docker run -p 8000:8000 --env-file .env swapi-voting-api](http://localhost:8000)
```

## 🌐 API Endpoints
Below is a reference of all available RESTful endpoints:

### 🟠 Import Endpoints

| Method | Path               | Description                         |
| ------ | ------------------ | ----------------------------------- |
| POST   | `/import/characters` | Import all characters from SWAPI   |
| POST   | `/import/films`      | Import all films from SWAPI        |
| POST   | `/import/starships`  | Import all starships from SWAPI    |

---

### 🟠 Characters

| Method | Path                          | Description                              |
| ------ | ----------------------------- | ---------------------------------------- |
| GET    | `/characters/`                | List all characters (paginated)         |
| GET    | `/characters/search`          | Search characters by name               |
| GET    | `/characters/{character_id}`  | Retrieve a single character by ID       |

---

### 🟠 Films

| Method | Path                     | Description                              |
| ------ | ------------------------ | ---------------------------------------- |
| GET    | `/films/`                | List all films (paginated)               |
| GET    | `/films/search`          | Search films by title                    |
| GET    | `/films/{film_id}`       | Retrieve a single film by ID             |

---

### 🟠 Starships

| Method | Path                          | Description                              |
| ------ | ----------------------------- | ---------------------------------------- |
| GET    | `/starships/`                 | List all starships (paginated)          |
| GET    | `/starships/search`           | Search starships by name                |
| GET    | `/starships/{starship_id}`    | Retrieve a single starship by ID        

---

### 📜 Documentation

| Method | Path     | Description                                             |
| ------ | -------- | ------------------------------------------------------- |
| GET    | `/docs`  | Interactive Swagger UI for all API endpoints           |
| GET    | `/redoc` | Alternative ReDoc documentation view                    |

✅ **Tip:** Explore and test all routes interactively at **/docs**.


## 👨‍💻 Author & Maintainer  
Thomas Bournaveas  
📧 thomas.bournaveas@gmail.com  
🔗 https://thomasbournaveas.com/