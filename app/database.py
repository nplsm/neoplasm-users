from motor import motor_asyncio

from .settings import settings

client = motor_asyncio.AsyncIOMotorClient(settings.mongo_url)
db = client[settings.mongo_db_name]
collection = db[settings.mongo_collection_name]
