from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database.models import UserSessionModel
from app.domain.user import UserSession


class AuthSessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, user_session: UserSession) -> UserSession:
        model = UserSessionModel.from_domain(user_session)
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return model.to_domain()

    def get_by_token_hash(self, token_hash: str) -> UserSession | None:
        statement = select(UserSessionModel).where(UserSessionModel.token_hash == token_hash)
        model = self.db.scalar(statement)
        return model.to_domain() if model else None

    def delete_expired(self, now: datetime) -> None:
        statement = delete(UserSessionModel).where(UserSessionModel.expires_at < now)
        self.db.execute(statement)

    def delete_by_token_hash(self, token_hash: str) -> None:
        statement = delete(UserSessionModel).where(UserSessionModel.token_hash == token_hash)
        self.db.execute(statement)
