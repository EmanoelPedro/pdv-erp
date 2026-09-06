from typing import Annotated

from fastapi import APIRouter, Depends, Header, Response, status

from app.api.dependencies import get_auth_service, get_current_user, get_optional_current_user
from app.domain.exceptions import AuthenticationRequiredError, OwnerPermissionRequiredError
from app.domain.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterUserRequest,
    SetupStateResponse,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/setup-state", response_model=SetupStateResponse)
def get_setup_state(
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SetupStateResponse:
    return SetupStateResponse(has_users=service.has_users())


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: RegisterUserRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
) -> UserResponse:
    if service.has_users() and current_user is None:
        raise AuthenticationRequiredError("Authentication is required.")
    if current_user is not None and current_user.role.value != "OWNER":
        raise OwnerPermissionRequiredError("Owner approval is required for this action.")

    user = service.register_user(
        full_name=payload.full_name,
        username=payload.username,
        pin=payload.pin,
        role=payload.role,
        actor=current_user,
    )
    return UserResponse.from_domain(user)


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponse:
    access_token, user = service.login(payload.username, payload.pin)
    return LoginResponse(access_token=access_token, user=UserResponse.from_domain(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    service: Annotated[AuthService, Depends(get_auth_service)] = None,
) -> Response:
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        if token:
            service.logout(token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserResponse)
def me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    return UserResponse.from_domain(current_user)


@router.get("/users", response_model=list[UserResponse])
def list_users(
    service: Annotated[AuthService, Depends(get_auth_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[UserResponse]:
    return [UserResponse.from_domain(user) for user in service.list_users(current_user)]
