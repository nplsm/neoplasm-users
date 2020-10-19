from app.hashing import crypt_context
from app.settings import settings
from app.tokens import get_refresh_token


def test_renew_tokens(register, tokens_renewal, test_token, collection):
    register_data = register(
        {
            "userInput": {
                "email": "test@neoplasm.xyz",
                "password1": "strong_password",
                "password2": "strong_password",
            }
        }
    )
    user_id = register_data["user"]["id"]
    register_refresh_token = register_data["tokens"]["refreshToken"]
    register_access_token = register_data["tokens"]["accessToken"]

    response = tokens_renewal({"refreshToken": register_refresh_token})
    assert response.ok

    user = collection.find_one()

    data = response.json()["data"]["renewTokens"]
    access_token = data["accessToken"]
    refresh_token = data["refreshToken"]

    assert crypt_context.verify(
        refresh_token,
        user["hashed_refresh_token"],
    )
    assert access_token != register_access_token
    assert refresh_token != register_refresh_token

    test_token(
        access_token,
        settings.access_token_secret,
        str(user_id),
        settings.access_token_expiration_timedelta,
    )
    test_token(
        refresh_token,
        settings.refresh_token_secret,
        str(user_id),
        settings.refresh_token_expiration_timedelta,
    )


def test_renew_tokens_error_bad_token(tokens_renewal, collection):
    response = tokens_renewal({"refreshToken": "bad_token"})
    assert response.ok

    data = response.json()["data"]["renewTokens"]
    assert not data


def test_renew_tokens_error_wrong_user(tokens_renewal):
    refresh_token = get_refresh_token("wrong_user_id")
    response = tokens_renewal({"refreshToken": refresh_token})
    assert response.ok

    data = response.json()["data"]["renewTokens"]
    assert not data
