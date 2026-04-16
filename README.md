# SafeHer - Women Safety Platform Backend 🛡️

[![Docker](https://img.shields.io/badge/Docker-Containerized-blue?logo=docker)](https://docker.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql)](https://postgresql.org/)

## ✅ Completed Features

- User Registration & Login (email/password)
- JWT Authentication
- Anonymous Incident Reporting
- Report Categories (Harassment, Stalking, Assault, etc.)
- Location-based Reports (latitude/longitude)
- Upvote System
- Admin Report Approval Workflow
- PostgreSQL Database with asyncpg
- API Documentation (Swagger)
- Docker Containerization

## 🛠️ Tech Stack

- FastAPI + asyncpg
- PostgreSQL + PostGIS ready
- SQLAlchemy (async)
- JWT + bcrypt
- Docker & Docker Compose

## 🐳 Quick Start with Docker (Easiest)

```bash
# Clone
git clone https://github.com/aayma-dev/SafeHer-backend.git
cd SafeHer-backend

# Start everything (backend + PostgreSQL)
docker-compose up --build
Then open: http://localhost:8000/api/docs

🚀 Manual Setup (Without Docker)
bash
# Clone
git clone https://github.com/aayma-dev/SafeHer-backend.git
cd SafeHer-backend

# Setup virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup database
psql -U postgres -c "CREATE DATABASE safeher_db;"

# Create .env file
# DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/safeher_db

# Initialize database
python init_db.py

# Run server
uvicorn app.main:app --reload
📚 API Endpoints
Method	Endpoint	Description
POST	/api/auth/register	Create account
POST	/api/auth/login	Login
GET	/api/auth/me	Get profile
POST	/api/reports/	Submit report
GET	/api/reports/	List reports
GET	/api/reports/nearby	Find nearby incidents
POST	/api/reports/{id}/upvote	Upvote report
📝 Environment Variables
Create .env file:

text
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/safeher_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
🛑 Stop Docker
bash
docker-compose down
📄 License
MIT