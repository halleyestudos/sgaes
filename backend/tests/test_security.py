from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_hash_password_round_trip() -> None:
    password = "Senha@123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("outra-senha", hashed) is False


def test_create_access_token_contains_claims() -> None:
    token = create_access_token(sub="123", rede_id=7, perfil="gestor", escola_id=9)
    assert token
    claims = decode_access_token(token)
    assert claims["sub"] == "123"
    assert claims["rede_id"] == 7
    assert claims["perfil"] == "gestor"
    assert claims["escola_id"] == 9
