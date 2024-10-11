from app.auth.services import generate_jtw_data


def generate_user_auth_header(user_id: int) -> dict[str, str]:
    token = generate_jtw_data(user_id=user_id).access_token

    return auth_header(token)


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
