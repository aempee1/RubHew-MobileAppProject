import asyncio
from rubhew import config, models

if __name__ == "__main__":
    # Use the testing configuration
    settings = config.get_settings(testing=True)
    models.init_db(settings)
    
    # Recreate the tables in the test database
    asyncio.run(models.recreate_table())
