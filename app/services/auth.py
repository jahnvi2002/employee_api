from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth.jwt import create_access_token
from app.auth.password import hash_password, verify_password
from app.auth.validation import validate_password, validate_username
from app.models.user import User
from app.schemas.user import UserCreate


def register_user(
    user: UserCreate,
    db: Session
):
    # Validate authentication data
    validate_username(user.username)
    validate_password(user.password)

    # Check whether username already exists
    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user:
        return {
            "message": "Username already exists"
        }

    # Hash password before storing it
    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "username": new_user.username,
        "email": new_user.email
    }


def login_user(
    username: str,
    password: str,
    db: Session
):
    existing_user = db.query(User).filter(
        User.username == username
    ).first()

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    password_is_correct = verify_password(
        password,
        existing_user.hashed_password
    )

    if not password_is_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        existing_user.username
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }