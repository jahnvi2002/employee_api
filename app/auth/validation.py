from fastapi import HTTPException


def validate_username(username: str):
    if not username or not username.strip():
        raise HTTPException(
            status_code=400,
            detail="Username cannot be empty"
        )


def validate_password(password: str):
    if not password or len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters"
        )