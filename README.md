# ⚡ SWAPI Voting API

## 📚 Table of Contents
- [⚡ SWAPI Voting API](#-swapi-voting-api)
  - [📚 Table of Contents](#-table-of-contents)
  - [📄 Description](#-description)
  - [✅ Features](#-features)
  - [🔒 Security and Compliance](#-security-and-compliance)
  - [⚙️ Installation](#️-installation)
    - [Windows](#windows)
    - [MacOS / Linux](#macos--linux)
- [Clone the repository](#clone-the-repository)
- [Create and activate virtual environment](#create-and-activate-virtual-environment)
- [Install dependencies](#install-dependencies)
- [Run database migrations (example if using Alembic)](#run-database-migrations-example-if-using-alembic)
- [Start the server](#start-the-server)
  - [🌐 API Endpoints](#-api-endpoints)
  - [👨‍💻 Maintainers](#-maintainers)

---

## 📄 Description
The **SWAPI Voting API** is a RESTful microservice built with FastAPI that integrates with the public Star Wars API (SWAPI).  
It fetches, stores, and serves Star Wars characters, films, and starships in a local SQL database, providing search, pagination, and future voting capabilities.

Designed for robust integrations with frontend apps or fan projects.

---

## ✅ Features
- 🌌 Import Star Wars data from the public SWAPI.
- 🗄️ SQL database with relationships (Characters ↔ Films).
- 🔎 Paginated listing and search by name or title.
- 🗳️ Foundation for voting on favorites.
- ⚡ FastAPI-powered with async support.
- 📜 Auto-generated Swagger UI docs.

---

## 🔒 Security and Compliance
- 🛡️ Configurable CORS support for frontend domains.
- 🌍 Public access (no authentication).
- 🔐 Environment-based configuration for secure deployment.
- ✅ Graceful error handling with standardized responses.

---

## ⚙️ Installation

### Windows

```powershell
# Clone repository
git clone https://github.com/yourusername/swapi-voting-api.git
cd swapi-voting-api

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations (if using Alembic)
alembic upgrade head

# Start the FastAPI server
uvicorn src.main:app --reload

## MacOS / Linux

# Clone repository
git clone https://github.com/yourusername/swapi-voting-api.git
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

### MacOS / Linux

# Clone the repository
git clone https://github.com/yourusername/swapi-voting-api.git
cd swapi-voting-api

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations (example if using Alembic)
alembic upgrade head

# Start the server
uvicorn src.main:app --reload

## 🌐 API Endpoints
1. POST /import/characters
Description: Fetches characters from SWAPI and stores them in the database.
Response (202 Accepted):

```json
{ "message": "Character import started/completed." }
```

2. POST /import/films
Description: Fetches films from SWAPI and stores them in the database.
Response (202 Accepted):

```json
{ "message": "Film import started/completed." }
```

3. POST /import/starships
Description: Fetches starships from SWAPI and stores them in the database.
Response (202 Accepted):
```json
{ "message": "Starship import started/completed." }
```

4. GET /characters/
Description: Retrieves stored characters with pagination.
Query Parameters:

skip: int (default 0)

limit: int (default 20)

Response (200 OK):
```json
[
  {
    "id": 1,
    "name": "Luke Skywalker",
    "gender": "male",
    "birth_year": "19BBY",
    "films": [
      { "id": 1, "title": "A New Hope" }
    ]
  }
]
```

5. GET /films/
Description: Retrieves stored films with pagination.
Query Parameters:

skip: int (default 0)

limit: int (default 20)

Response (200 OK):
```json
[
  {
    "id": 1,
    "title": "A New Hope",
    "director": "George Lucas",
    "producer": "Gary Kurtz, Rick McCallum",
    "release_date": "1977-05-25",
    "characters": [
      { "id": 1, "name": "Luke Skywalker" }
    ]
  }
]
```

6. GET /starships/
Description: Retrieves stored starships with pagination.
Query Parameters:

skip: int (default 0)

limit: int (default 20)

Response (200 OK):
```json
[
  {
    "id": 1,
    "name": "Millennium Falcon",
    "model": "YT-1300 light freighter",
    "manufacturer": "Corellian Engineering Corporation",
    "starship_class": "Light freighter"
  }
]
```

7. GET /characters/search
Description: Search stored characters by name.
✅ Query Parameter:

q: str (search term)
✅ Response (200 OK):
```json
[
  { "id": 1, "name": "Luke Skywalker", "gender": "male", "birth_year": "19BBY", "films": [...] }
]
```

8. GET /characters/{character_id}
Description: Get a single character by ID.
✅ Response (200 OK):
```json
{
  "id": 1,
  "name": "Luke Skywalker",
  "gender": "male",
  "birth_year": "19BBY",
  "films": [...]
}
```

9. GET /films/search
Description: Search stored films by title.
✅ Query Parameter:

q: str (search term)
✅ Response (200 OK):
```json
[
  { "id": 1, "title": "A New Hope", "director": "George Lucas", ... }
]
```

10. GET /films/{film_id}
Description: Get a single film by ID.
✅ Response (200 OK):
```json
{
  "id": 1,
  "title": "A New Hope",
  "director": "George Lucas",
  "producer": "...",
  "release_date": "1977-05-25",
  "characters": [...]
}
```

11. GET /starships/search
Description: Search stored starships by name.
✅ Query Parameter:

q: str (search term)
✅ Response (200 OK):
```json
[
  { "id": 1, "name": "Millennium Falcon", "model": "...", ... }
]
```

12. GET /starships/{starship_id}
Description: Get a single starship by ID.
✅ Response (200 OK):
```json
{
  "id": 1,
  "name": "Millennium Falcon",
  "model": "...",
  "manufacturer": "...",
  "starship_class": "..."
}
```

13. GET /docs (Swagger UI)
Description: Provides interactive, auto-generated API documentation for exploring and testing all endpoints directly in the browser.
✅ URL: /docs
✅ Description: Auto-generated by FastAPI based on Pydantic models and response schemas.

---

## 👨‍💻 Maintainers
- **Author**: Thomas Bournaveas (tbournaveas@heron.gr)  
- **Maintained by**: Heron IT Development Team (IT-Delivery@heron.gr)

---