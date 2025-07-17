
# 🚀 FastAPI-LLM-Postgres Backend

![Screenshot](public/ss.png)

## 📁 Project Structure

The project follows a layered architecture to ensure clear separation of concerns, scalability, and maintainability.

```plaintext
.
├── .env                  
├── .gitignore            
├── Dockerfile            
├── pyproject.toml        
├── poetry.lock           
├── README.md             
├── alembic.ini           
├── migrations/           
│   ├── env.py            
│   ├── script.py.mako    
│   └── versions/         
│       └── <timestamp>_initial_ai_schema_and_tables.py
├── prompts/              
│   ├── generic_text_generation.jinja2
│   └── job_parser.jinja2
└── app/                  
    ├── main.py           
    ├── api/              
    │   └── v1/           
    │       ├── endpoints/
    │       │   ├── llm.py     
    │       │   └── data.py    
    │       └── dependencies.py
    ├── core/             
    │   ├── config.py     
    │   └── exceptions.py 
    ├── db/               
    │   ├── database.py   
    │   └── models.py     
    ├── llm_providers/    
    │   ├── base.py       
    │   ├── openai_provider.py 
    │   ├── gemini_provider.py 
    │   └── (other_providers.py)
    ├── models/           
    │   ├── llm_models.py 
    │   └── db_models.py  
    ├── services/         
    │   ├── llm_service.py 
    │   └── data_service.py 
    └── utils/            
        ├── logger.py     
        ├── prompt_manager.py 
        └── web_scraper.py 
```

## 🛠️ Setup Guide

### 1. Prerequisites

Ensure you have the following installed on your system:

- **Python 3.11+**
- **PostgreSQL**
- **Git**

### 2. Install Poetry

#### macOS / Linux / WSL

```bash
pipx install poetry
```

#### Windows (PowerShell)

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

Verify installation:

```bash
poetry --version
```

### 3. Clone the Repository

```bash
git clone https://github.com/mk-hasan/FastAPI-LLM-Postgres-Server.git
cd FastAPI-LLM-Postgres-Server.ai
```

### 4. Install Dependencies

```bash
poetry install
poetry shell
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY="sk-your-openai-api-key-here"
COHERE_API_KEY="your-cohere-api-key-here"
HUGGINGFACE_API_KEY="hf_your_huggingface_api_key"
GOOGLE_API_KEY="AIzaSy_your-gemini-api-key-here"
DEFAULT_LLM_PROVIDER="gemini"
POSTGRES_USER="local_user"
POSTGRES_PASSWORD="local_password"
POSTGRES_SERVER="localhost"
POSTGRES_PORT="5432"
POSTGRES_DB="ai_db"
```

### 6. Database Setup & Migrations

Create database and user:

You can quickly start a PostgreSQL database using Docker Compose:

```bash
docker-compose up -d postgres
```

This will start the PostgreSQL service defined in your `docker-compose.yaml`. Make sure your environment variables in `.env` match the credentials above.

---
Alternatively you can install postgres and execute this command
```sql
CREATE DATABASE ai_db;
CREATE USER local_user WITH PASSWORD 'local_password';
GRANT ALL PRIVILEGES ON DATABASE craidb TO local_user;
```

---



Clean Alembic State:

```bash
rm -rf migrations/versions/*
```

In PostgreSQL:

```sql
DROP TABLE IF EXISTS alembic_version;
DROP SCHEMA IF EXISTS db_ai CASCADE;
```

Reinitialize Alembic:

```bash
alembic init migrations
```

Edit `alembic.ini`:

```
sqlalchemy.url = postgresql+psycopg2://local_user:local_password@localhost:5432/craidb
```

Edit `migrations/env.py`:

```python
from app.db.database import Base
target_metadata = Base.metadata
```

Generate and apply migration:

```bash
alembic revision --autogenerate -m "Initial AI schema and tables"
alembic upgrade head
```

## 🚀 Running the Application

```bash
poetry shell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Visit [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs) to explore the interactive OpenAPI docs.

## 🧪 API Endpoints & Testing

### 1. LLM Generation & Parsing

**POST /api/v1/llm/generate**

```json
{
  "request": {
    "prompt": "Explain quantum entanglement in two sentences.",
    "llm_provider": "gemini",
    "max_tokens": 100,
    "temperature": 0.5
  },
  "use_cache": true,
  "cache_ttl_minutes": 60
}
```

**POST /api/v1/llm/parse-job**

```json
{
  "job_url": "https://careers.google.com/jobs/results/1234567890/software-engineer-mountain-view-ca/",
  "llm_provider": "gemini"
}
```

### 2. Data Management

**POST /api/v1/data/users**

```json
{
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "is_active": true
}
```

**GET /api/v1/data/users/{user_id}**

Example: `http://0.0.0.0:8000/api/v1/data/users/1`

**GET /api/v1/data/users?skip=0&limit=10**

## 🤝 Contributing

Create A PR with your changes!
