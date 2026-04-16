# SafeHer - Women Safety Platform Backend 🛡️

## ✅ Completed Features

- User Registration & Login
- JWT Authentication
- Password Validation (uppercase, lowercase, number, special char)
- PostgreSQL Database
- API Documentation (Swagger)

## 🛠️ Tech Stack

- FastAPI
- PostgreSQL + asyncpg
- SQLAlchemy (async)
- JWT + bcrypt

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/SafeHer-backend.git
cd SafeHer-backend

# Setup virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup database
psql -U postgres -c "CREATE DATABASE safeher_db;"

# Create .env file and add your database URL
# DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/safeher_db

# Initialize database
python init_db.py

# Run server
uvicorn app.main:app --reload
