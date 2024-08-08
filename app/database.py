from motor.motor_asyncio import AsyncIOMotorClient

from app.config import DATABASE_URL, DATABASE_NAME

# Initialize the MongoDB client and database
client = AsyncIOMotorClient(DATABASE_URL)
db = client[DATABASE_NAME]


# Function to get the database instance
def get_database():
    return db
