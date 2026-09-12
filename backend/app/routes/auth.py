"""Authentication routes."""

from flask import Blueprint, request
from flask_jwt_extended import create_access_token

from app.errors.api_error import ApiError
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import authenticate_user, register_user
from app.utils.responses import success_response

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    """Authenticate by username or email and return a JWT access token."""
    login_request = LoginRequest.model_validate(request.get_json())

    user = authenticate_user(login_request.identifier, login_request.password)

    if user is None:
        raise ApiError("INVALID_CREDENTIALS", "Invalid identifier or password.", 401)

    access_token = create_access_token(identity=str(user.id))

    return success_response({"access_token": access_token, "user": user.to_dict()})


@auth_bp.post("/register")
def register():
    """Create an account and return a token"""
    register_request = RegisterRequest.model_validate(request.get_json())

    user = register_user(
        username=register_request.username,
        email=register_request.email,
        password=register_request.password,
    )

    access_token = create_access_token(identity=str(user.id))

    return success_response(
        {"access_token": access_token, "user": user.to_dict()}, 201
    )
