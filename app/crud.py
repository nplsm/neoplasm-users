from typing import Optional

from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument
from pymongo.results import InsertOneResult

from .database import collection
from .models import User, UserSave


async def get_user_by_id(
    user_id: ObjectId,
    collection: AsyncIOMotorCollection = collection,
) -> Optional[User]:
    user_data = await collection.find_one({"_id": user_id})
    if user_data:
        return User(**user_data)
    return None


async def get_user_by_email(
    email: str,
    collection: AsyncIOMotorCollection = collection,
) -> Optional[User]:
    user_data = await collection.find_one({"email": email})
    if user_data:
        return User(**user_data)
    return None


async def create_user(
    user_data: UserSave,
    collection: AsyncIOMotorCollection = collection,
) -> User:
    result: InsertOneResult = await collection.insert_one(user_data.dict())
    user_result = await get_user_by_id(result.inserted_id)
    if user_result:
        return user_result
    raise Exception


async def update_user(
    user_id: ObjectId,
    user_data: UserSave,
    collection: AsyncIOMotorCollection = collection,
) -> Optional[User]:
    user_result = await collection.find_one_and_update(
        {"_id": user_id},
        user_data.dict(),
        return_document=ReturnDocument.AFTER,
    )
    return User(**user_result)
