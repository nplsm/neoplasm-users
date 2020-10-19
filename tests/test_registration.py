from datetime import datetime

from jose import jwt

from app.hashing import crypt_context
from app.settings import settings

query = """
    mutation($userInput: UserRegister!) {
        register(userInput: $userInput) {
            error
            user {
                id
                email
            }
            tokens {
                accessToken
                refreshToken
            }
        }
    }
"""


def test_registration(test_client, test_collection):
    variables = {
        "userInput": {
            "email": "test@neoplasm.xyz",
            "password1": "strong_password",
            "password2": "strong_password",
        }
    }

    r = test_client.post("/", json={"query": query, "variables": variables})
    assert r.ok

    user = test_collection.find_one()
    assert user["_id"]
    assert user["email"] == "test@neoplasm.xyz"
    assert crypt_context.verify(
        "strong_password",
        user["hashed_password"],
    )
    assert user["registration_datetime"] < datetime.utcnow()
    assert user["hashed_refresh_token"]

    data = r.json()["data"]["register"]
    assert not data["error"]
    assert data["user"]["id"] == str(user["_id"])
    assert data["user"]["email"] == "test@neoplasm.xyz"
    assert crypt_context.verify(
        data["tokens"]["refreshToken"],
        user["hashed_refresh_token"],
    )

    access_token_payload = jwt.decode(
        data["tokens"]["accessToken"],
        settings.access_token_secret,
        algorithms=[settings.token_algorithm],
    )
    assert access_token_payload["iss"] == settings.token_iss
    assert access_token_payload["sub"] == str(user["_id"])
    access_expiration = datetime.utcfromtimestamp(access_token_payload["exp"])
    access_issued_at = datetime.utcfromtimestamp(access_token_payload["iat"])
    assert access_issued_at < datetime.utcnow()
    access_timedelta = access_expiration - access_issued_at
    assert access_timedelta == settings.access_token_expiration_timedelta

    refresh_token_payload = jwt.decode(
        data["tokens"]["refreshToken"],
        settings.refresh_token_secret,
        algorithms=[settings.token_algorithm],
    )
    assert refresh_token_payload["iss"] == settings.token_iss
    assert refresh_token_payload["sub"] == str(user["_id"])
    refresh_expiration = datetime.utcfromtimestamp(refresh_token_payload["exp"])
    refresh_issued_at = datetime.utcfromtimestamp(refresh_token_payload["iat"])
    assert refresh_issued_at < datetime.utcnow()
    refresh_timedelta = refresh_expiration - refresh_issued_at
    assert refresh_timedelta == settings.refresh_token_expiration_timedelta


def test_registration_error_email_already_registered(test_client, test_collection):
    variables = {
        "userInput": {
            "email": "test@neoplasm.xyz",
            "password1": "strong_password",
            "password2": "strong_password",
        }
    }

    test_client.post("/", json={"query": query, "variables": variables})
    r = test_client.post("/", json={"query": query, "variables": variables})

    assert r.ok

    data = r.json()["data"]["register"]
    assert data["error"] == "Email already registered"
    assert not data["user"]
    assert not data["tokens"]


def test_registration_error_weak_password(test_client):
    variables = {
        "userInput": {
            "email": "test@neoplasm.xyz",
            "password1": "pwd",
            "password2": "pwd",
        }
    }

    r = test_client.post("/", json={"query": query, "variables": variables})

    assert r.ok

    data = r.json()["data"]["register"]
    assert data["error"] == "Bad credentials"
    assert not data["user"]
    assert not data["tokens"]


def test_registration_error_passwords_dont_match(test_client):
    variables = {
        "userInput": {
            "email": "test@neoplasm.xyz",
            "password1": "strong_password",
            "password2": "wrong_password",
        }
    }

    r = test_client.post("/", json={"query": query, "variables": variables})

    assert r.ok

    data = r.json()["data"]["register"]
    assert data["error"] == "Bad credentials"
    assert not data["user"]
    assert not data["tokens"]


def test_registration_error_invalid_email(test_client):
    variables = {
        "userInput": {
            "email": "testneoplasmxyz",
            "password1": "strong_password",
            "password2": "strong_password",
        }
    }

    r = test_client.post("/", json={"query": query, "variables": variables})

    assert r.ok

    data = r.json()["data"]["register"]
    assert data["error"] == "Bad credentials"
    assert not data["user"]
    assert not data["tokens"]
