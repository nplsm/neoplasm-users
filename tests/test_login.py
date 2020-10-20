from app.hashing import crypt_context
from app.settings import settings


def test_login(register, login, collection, test_token):
    register_data = register(
        {
            "userInput": {
                "email": "test@neoplasm.xyz",
                "password1": "strong_password",
                "password2": "strong_password",
            }
        }
    )
    register_user = register_data["user"]
    user_id = register_user["id"]
    user_email = register_user["email"]

    response = login(
        {
            "userInput": {
                "email": user_email,
                "password": "strong_password",
            }
        }
    )
    assert response.ok

    user = collection.find_one()

    data = response.json()["data"]["login"]
    assert not data["error"]
    assert data["user"]["id"] == user_id
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


def test_login_error_wrong_email(login):
    response = login(
        {
            "userInput": {
                "email": "test@neoplasm.xyz",
                "password": "strong_password",
            }
        }
    )
    assert response.ok

    data = response.json()["data"]["login"]
    assert data["error"] == "Wrong email"
    assert not data["user"]
    assert not data["tokens"]


def test_login_error_wrong_password(register, login):
    register(
        {
            "userInput": {
                "email": "test@neoplasm.xyz",
                "password1": "strong_password",
                "password2": "strong_password",
            }
        }
    )

    response = login(
        {
            "userInput": {
                "email": "test@neoplasm.xyz",
                "password": "wrong_password",
            }
        }
    )
    assert response.ok

    data = response.json()["data"]["login"]
    assert data["error"] == "Wrong password"
    assert not data["user"]
    assert not data["tokens"]


def test_login_error_wrong_credentials(login):
    response = login(
        {
            "userInput": {
                "email": "not_email",
                "password": "strong_password",
            }
        }
    )
    assert response.ok

    data = response.json()["data"]["login"]
    assert data["error"] == "Credentials are not valid"
    assert not data["user"]
    assert not data["tokens"]
