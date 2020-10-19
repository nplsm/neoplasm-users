from datetime import datetime

from app.hashing import crypt_context
from app.settings import settings


def test_registration(registration, collection, test_token):
    response = registration(
        {
            "userInput": {
                "email": "test@neoplasm.xyz",
                "password1": "strong_password",
                "password2": "strong_password",
            }
        }
    )
    assert response.ok

    user = collection.find_one()
    user_id = user["_id"]
    user_email = user["email"]

    assert user_id
    assert user_email == "test@neoplasm.xyz"
    assert crypt_context.verify(
        "strong_password",
        user["hashed_password"],
    )
    assert user["registration_datetime"] < datetime.utcnow()
    assert user["hashed_refresh_token"]

    data = response.json()["data"]["register"]
    assert not data["error"]
    assert data["user"]["id"] == str(user_id)
    assert data["user"]["email"] == user_email
    assert crypt_context.verify(
        data["tokens"]["refreshToken"],
        user["hashed_refresh_token"],
    )
    test_token(
        data["tokens"]["accessToken"],
        settings.access_token_secret,
        str(user_id),
        settings.access_token_expiration_timedelta,
    )
    test_token(
        data["tokens"]["refreshToken"],
        settings.refresh_token_secret,
        str(user_id),
        settings.refresh_token_expiration_timedelta,
    )


def test_registration_error_email_already_registered(registration, collection):
    variables = {
        "userInput": {
            "email": "test@neoplasm.xyz",
            "password1": "strong_password",
            "password2": "strong_password",
        }
    }

    registration(variables)
    response = registration(variables)
    assert response.ok

    data = response.json()["data"]["register"]
    assert data["error"] == "Email already registered"
    assert not data["user"]
    assert not data["tokens"]


def test_registration_error_weak_password(registration):
    response = registration(
        {
            "userInput": {
                "email": "test@neoplasm.xyz",
                "password1": "pwd",
                "password2": "pwd",
            }
        }
    )
    assert response.ok

    data = response.json()["data"]["register"]
    assert data["error"] == "Bad credentials"
    assert not data["user"]
    assert not data["tokens"]


def test_registration_error_passwords_dont_match(registration):
    response = registration(
        {
            "userInput": {
                "email": "test@neoplasm.xyz",
                "password1": "strong_password",
                "password2": "wrong_password",
            }
        }
    )
    assert response.ok

    data = response.json()["data"]["register"]
    assert data["error"] == "Bad credentials"
    assert not data["user"]
    assert not data["tokens"]


def test_registration_error_invalid_email(registration):
    response = registration(
        {
            "userInput": {
                "email": "testneoplasmxyz",
                "password1": "strong_password",
                "password2": "strong_password",
            }
        }
    )
    assert response.ok

    data = response.json()["data"]["register"]
    assert data["error"] == "Bad credentials"
    assert not data["user"]
    assert not data["tokens"]
