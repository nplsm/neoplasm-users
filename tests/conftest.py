from datetime import datetime, timedelta
from typing import Callable

import pytest
from jose import jwt
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from requests import Response
from starlette.testclient import TestClient

from app.main import app
from app.settings import settings


@pytest.fixture()
def db() -> Database:
    client = MongoClient(settings.mongo_url)
    db_name = settings.mongo_db_name
    db = client[db_name]
    client.drop_database(db)
    yield db
    client.drop_database(db)


@pytest.fixture()
def collection(db: Database) -> Collection:
    collection_name = settings.mongo_collection_name
    collection = db[collection_name]
    collection.drop()
    collection.create_index("email", unique=True)
    yield collection
    collection.drop()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def test_token() -> Callable[[str, str, str, timedelta, str, str], None]:
    def _test_token(
        token: str,
        secret: str,
        subscriber: str,
        expirtion_timedelta: timedelta,
        issuer: str = settings.token_iss,
        algorithm: str = settings.token_algorithm,
    ):
        payload = jwt.decode(
            token,
            secret,
            algorithms=[algorithm],
        )
        assert payload["iss"] == issuer
        assert payload["sub"] == subscriber
        expiration = datetime.utcfromtimestamp(payload["exp"])
        issued_at = datetime.utcfromtimestamp(payload["iat"])
        assert issued_at < datetime.utcnow()
        assert expiration - issued_at == expirtion_timedelta

    return _test_token


@pytest.fixture()
def post(client) -> Callable[[str, dict], Response]:
    def _post(query: str, variables: dict) -> Response:
        return client.post("/", json={"query": query, "variables": variables})

    return _post


@pytest.fixture()
def registration(post: Callable[[str, dict], Response]) -> Callable[[dict], Response]:
    def _registration(variables: dict) -> Response:
        with open("tests/mutations/registration.gql") as f:
            query = f.read()
        return post(query, variables)

    return _registration


@pytest.fixture()
def register(registration: Callable[[dict], Response]) -> Callable[[dict], dict]:
    def _register(variables: dict) -> dict:
        response = registration(variables)
        assert response.ok
        return response.json()["data"]["register"]

    return _register


@pytest.fixture()
def tokens_renewal(post: Callable[[str, dict], Response]) -> Callable[[dict], Response]:
    def _tokens_renewal(variables: dict) -> Response:
        with open("tests/mutations/token_renewal.gql") as f:
            query = f.read()
        return post(query, variables)

    return _tokens_renewal


@pytest.fixture()
def login(post: Callable[[str, dict], Response]) -> Callable[[dict], Response]:
    def _login(variables: dict) -> Response:
        with open("tests/mutations/login.gql") as f:
            query = f.read()
        return post(query, variables)

    return _login
