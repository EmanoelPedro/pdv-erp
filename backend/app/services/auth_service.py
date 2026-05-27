from datetime import timedelta

from app.domain.exceptions import (
    AuthenticationRequiredError,
    DuplicateUsernameError,
    InvalidCredentialsError,
    OwnerPermissionRequiredError,
    UserNotFoundError,
    UserRegistrationNotAllowedError,
)
from app.domain.shared import utc_now
from app.domain.user import User, UserRole, UserSession
from app.repositories.auth_session_repository import AuthSessionRepository
from app.repositories.user_repository import UserRepository
from app.services.security import (
    generate_access_token,
    hash_access_token,
    hash_pin,
    verify_pin,
)


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        auth_session_repository: AuthSessionRepository,
        session_days: int,
    ) -> None:
        self.user_repository = user_repository
        self.auth_session_repository = auth_session_repository
        self.session_days = session_days

    def has_users(self) -> bool:
        return self.user_repository.count() > 0

    def register_user(
        self,
        full_name: str,
        username: str,
        pin: str,
        role: UserRole | None,
        actor: User | None,
    ) -> User:
        normalized_username = username.strip().lower()
        if self.user_repository.get_by_username(normalized_username) is not None:
            raise DuplicateUsernameError("This username is already in use.")

        user_count = self.user_repository.count()
        if user_count == 0:
            target_role = UserRole.OWNER
        else:
            if actor is None or actor.role != UserRole.OWNER:
                raise UserRegistrationNotAllowedError(
                    "Only the owner can create more users.",
                )
            target_role = role or UserRole.EMPLOYEE

        user = User.create(
            full_name=full_name.strip(),
            username=normalized_username,
            role=target_role,
            pin_hash=hash_pin(pin),
        )
        try:
            created_user = self.user_repository.create(user)
            self.user_repository.db.commit()
            return created_user
        except Exception:
            self.user_repository.db.rollback()
            raise

    def login(self, username: str, pin: str) -> tuple[str, User]:
        normalized_username = username.strip().lower()
        user = self.user_repository.get_by_username(normalized_username)
        if user is None or not user.is_active or not verify_pin(pin, user.pin_hash):
            raise InvalidCredentialsError("Invalid username or PIN.")

        now = utc_now()
        token = generate_access_token()
        token_hash = hash_access_token(token)
        user_session = UserSession.create(
            user_id=user.id,
            token_hash=token_hash,
            created_at=now,
            expires_at=now + timedelta(days=self.session_days),
        )
        try:
            self.auth_session_repository.delete_expired(now)
            self.auth_session_repository.create(user_session)
            self.auth_session_repository.db.commit()
            return token, user
        except Exception:
            self.auth_session_repository.db.rollback()
            raise

    def authenticate(self, token: str) -> User:
        token_hash = hash_access_token(token)
        session = self.auth_session_repository.get_by_token_hash(token_hash)
        if session is None:
            raise AuthenticationRequiredError("Authentication is required.")

        if session.expires_at < utc_now():
            self.auth_session_repository.delete_by_token_hash(token_hash)
            self.auth_session_repository.db.commit()
            raise AuthenticationRequiredError("Authentication is required.")

        user = self.user_repository.get_by_id(session.user_id)
        if user is None:
            raise UserNotFoundError("User was not found.")
        if not user.is_active:
            raise AuthenticationRequiredError("Authentication is required.")

        return user

    def logout(self, token: str) -> None:
        token_hash = hash_access_token(token)
        try:
            self.auth_session_repository.delete_by_token_hash(token_hash)
            self.auth_session_repository.db.commit()
        except Exception:
            self.auth_session_repository.db.rollback()
            raise

    def require_owner(self, user: User) -> None:
        if user.role != UserRole.OWNER:
            raise OwnerPermissionRequiredError(
                "Owner approval is required for this action.",
            )

    def list_users(self, actor: User) -> list[User]:
        self.require_owner(actor)
        return self.user_repository.list_all()
