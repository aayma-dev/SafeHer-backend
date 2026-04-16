import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.models import Base

async def init_db():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Create all tables (users, user_sessions, reports)
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully!")
        print("   - users table")
        print("   - user_sessions table")
        print("   - reports table")
    
    await engine.dispose()
    print("\n✅ Database setup complete!")

if __name__ == "__main__":
    asyncio.run(init_db())