from typing import Any, Optional

from ariadne import MutationType, QueryType, convert_kwargs_to_snake_case
from ariadne.contrib.federation import FederatedObjectType
from ariadne.types import GraphQLResolveInfo
from bson.objectid import ObjectId
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

from .crud import create_user, get_user_by_email, get_user_by_id
from .hashing import get_hash, verify_password
from .models import Tokens, User, UserLogin, UserPayload, UserRegister, UserSave
from .tokens import get_tokens_and_add_refresh_token_to_db, renew_tokens

query = QueryType()
mutation = MutationType()
user = FederatedObjectType("User")


@user.reference_resolver
async def resolve_user_reference(
    obj: Any,
    info: GraphQLResolveInfo,
    representation: dict,
) -> Optional[User]:
    user_id = ObjectId(representation["id"])
    if user_id:
        return await get_user_by_id(user_id)
    return None


@query.field("me")
async def me(
    obj: Any,
    info: GraphQLResolveInfo,
) -> Optional[User]:
    user_id = ObjectId(info.context["userId"])
    if user_id:
        return await get_user_by_id(user_id)
    return None


@mutation.field("register")
@convert_kwargs_to_snake_case
async def resolve_register(
    obj: Any,
    info: GraphQLResolveInfo,
    user_input: dict,
) -> UserPayload:
    try:
        user_data = UserRegister(**user_input)
        hashed_password = get_hash(user_data.password1)
        user_to_create = UserSave(
            hashed_password=hashed_password,
            **user_data.dict(),
        )
        user = await create_user(user_to_create)
        tokens = await get_tokens_and_add_refresh_token_to_db(user.id)
        payload = UserPayload.construct(user=user, tokens=tokens)
    except DuplicateKeyError:
        error = "Email already registered"
        payload = UserPayload.construct(error=error)
    except ValidationError:
        error = "Bad credentials"
        payload = UserPayload.construct(error=error)
    return payload


@mutation.field("login")
@convert_kwargs_to_snake_case
async def resolve_login(
    obj: Any,
    info: GraphQLResolveInfo,
    user_input: dict,
) -> UserPayload:
    try:
        user_data = UserLogin(**user_input)
        user = await get_user_by_email(user_data.email)
        if user:
            password_is_correct = await verify_password(user_data.password, user)
            if password_is_correct:
                tokens = await get_tokens_and_add_refresh_token_to_db(user.id)
                payload = UserPayload.construct(user=user, tokens=tokens)
            else:
                error = "Wrong password"
                payload = UserPayload.construct(error=error)
        else:
            error = "Wrong email"
            payload = UserPayload.construct(error=error)
    except ValidationError:
        error = "Credentials are not valid"
        payload = UserPayload.construct(error=error)
    return payload


@mutation.field("renewTokens")
@convert_kwargs_to_snake_case
async def resolve_renew_tokens(
    obj: Any,
    info: GraphQLResolveInfo,
    refresh_token: str,
) -> Optional[Tokens]:
    return await renew_tokens(refresh_token)
