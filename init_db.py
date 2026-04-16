import asyncio
import time
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.models import Base

async def init_db():
    # Wait for database to be ready (important for Docker)
    print("Waiting for database to be ready...")
    for i in range(30):
        try:
            engine = create_async_engine(settings.DATABASE_URL, echo=True)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables created successfully!")
            print("   - users table")
            print("   - user_sessions table")
            print("   - reports table")
            await engine.dispose()
            return
        except Exception as e:
            print(f"Waiting for database... ({i+1}/30)")
            time.sleep(2)
    
    print("❌ Could not connect to database")
    raise Exception("Database connection failed")

if __name__ == "__main__":
    asyncio.run(init_db())