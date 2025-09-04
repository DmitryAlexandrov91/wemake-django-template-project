def get_user_json(email: str, password: str) -> dict[str, str]:
    """Return json for authentication."""
    return {
        'email': email,
        'password': password,
    }
