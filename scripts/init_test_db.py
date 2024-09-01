# scripts/init_test_db.py

import asyncio
from sqlmodel import SQLModel
from rubhew.config import get_settings
from rubhew.models import init_db, engine

async def init_db_async():
    # Get settings for the test database
    settings = get_settings(testing=True)
    print(f"Settings: {settings.SQLDB_URL}")
    
    # Initialize the database engine with test settings
    init_db(settings)
    
    # Check if the engine is properly initialized
    if engine is None:
        raise Exception("Database engine is not initialized.")
    
    print("Engine initialized successfully.")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("Tables created successfully.")

# Run the async function to initialize the test database
if __name__ == "__main__":
    asyncio.run(init_db_async())
    print("Test database (test.db) created successfully.")
