from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from bson.objectid import ObjectId
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorCollection
from passlib.context import CryptContext

from .crud import get_user_by_id
from .database import collection
from .hashing import crypt_context, get_hash
from .models import Tokens
from .settings import settings


def get_token(
    user_id: ObjectId,
    secret: str,
    expirtion_timedelta: timedelta,
    issuer: str = settings.token_iss,
    algorithm: str = settings.token_algorithm,
) -> str:
    issued_at = datetime.utcnow()
    expiration = issued_at + expirtion_timedelta
    payload = {
        "iss": issuer,
        "sub": str(user_id),
        "exp": expiration,
        "iat": issued_at,
        "jti": uuid4().hex,
    }
    token = jwt.encode(
        payload,
        secret,
        algorithm=algorithm,
    )
    return token


def get_access_token(
    user_id: ObjectId,
    secret: str = settings.access_token_secret,
    expirtion_timedelta: timedelta = settings.access_token_expiration_timedelta,
) -> str:
    token = get_token(user_id, secret, expirtion_timedelta)
    return token


def get_refresh_token(
    user_id: ObjectId,
    secret: str = settings.refresh_token_secret,
    expirtion_timedelta: timedelta = settings.refresh_token_expiration_timedelta,
) -> str:
    token = get_token(user_id, secret, expirtion_timedelta)
    return token


def get_tokens(user_id: ObjectId) -> Tokens:
    access_token = get_access_token(user_id)
    refresh_token = get_refresh_token(user_id)
    tokens = Tokens(
        access_token=access_token,
        refresh_token=refresh_token,
    )
    return tokens


async def get_tokens_and_add_refresh_token_to_db(
    user_id: ObjectId,
    collection: AsyncIOMotorCollection = collection,
) -> Tokens:
    tokens = get_tokens(user_id)
    hashed_refresh_token = get_hash(tokens.refresh_token)
    await collection.find_one_and_update(
        {"_id": user_id},
        {"$set": {"hashed_refresh_token": hashed_refresh_token}},
    )
    return tokens


async def renew_tokens(
    refresh_token: str,
    secret: str = settings.refresh_token_secret,
    issuer: str = settings.token_iss,
    algorithm: str = settings.token_algorithm,
    collection: AsyncIOMotorCollection = collection,
    context: CryptContext = crypt_context,
) -> Optional[Tokens]:
    try:
        payload = jwt.decode(
            refresh_token,
            secret,
            algorithms=[algorithm],
            issuer=issuer,
        )
        if "sub" in payload:
            user_id = ObjectId(payload["sub"])
            user = await get_user_by_id(user_id)
            if (
                user
                and user.hashed_refresh_token
                and context.verify(refresh_token, user.hashed_refresh_token)
            ):
                tokens = await get_tokens_and_add_refresh_token_to_db(user_id)
                return tokens
        return None
    except JWTError:
        return None
