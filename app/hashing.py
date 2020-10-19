from motor.motor_asyncio import AsyncIOMotorCollection
from passlib.context import CryptContext

from .database import collection
from .models import User

crypt_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


def get_hash(secret: str, context: CryptContext = crypt_context) -> str:
    return context.hash(secret)


async def verify_password(
    password: str,
    user: User,
    context: CryptContext = crypt_context,
    collection: AsyncIOMotorCollection = collection,
) -> bool:
    verified, new_hashed_password = context.verify_and_update(
        password, user.hashed_password
    )
    if verified:
        if new_hashed_password:
            await collection.find_one_and_update(
                {"_id": user.id},
                {"$set": {"hashed_password": new_hashed_password}},
            )
        return True
    return False
