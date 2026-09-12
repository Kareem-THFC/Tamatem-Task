"""Validation schemas for authentication requests."""

from typing import Annotated

from pydantic import BaseModel, EmailStr, StringConstraints

MAX_USERNAME_LENGTH = 80
MIN_USERNAME_LENGTH = 3

MAX_EMAIL_LENGTH = 255

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


class LoginRequest(BaseModel):
    """The JSON payload accepted by the login endpoint."""

    identifier: Annotated[
        str,
        StringConstraints(
            strict=True,
            strip_whitespace=True,
            min_length=1,
            max_length=255,
        ),
    ]
    password: Annotated[
        str,
        StringConstraints(strict=True, min_length=1, max_length=128),
    ]


class RegisterRequest(BaseModel):
    """The JSON payload accepted by ``POST /api/auth/register``.
    """

    username: Annotated[
        str,
        StringConstraints(
            strict=True,
            strip_whitespace=True,
            min_length=MIN_USERNAME_LENGTH,
            max_length=MAX_USERNAME_LENGTH,
            pattern=r"^[A-Za-z0-9._-]+$",
        ),
    ]

    
    email: Annotated[
        EmailStr,
        StringConstraints(
            strip_whitespace=True, to_lower=True, max_length=MAX_EMAIL_LENGTH
        ),
    ]

    password: Annotated[
        str,
        StringConstraints(
            strict=True,
            min_length=MIN_PASSWORD_LENGTH,
            max_length=MAX_PASSWORD_LENGTH,
        ),
    ]
