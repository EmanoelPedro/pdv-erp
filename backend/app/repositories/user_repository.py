from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models import UserModel
from app.domain.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def count(self) -> int:
        statement = select(func.count()).select_from(UserModel)
        return int(self.db.scalar(statement) or 0)

    def create(self, user: User) -> User:
        model = UserModel.from_domain(user)
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return model.to_domain()

    def get_by_username(self, username: str) -> User | None:
        statement = select(UserModel).where(UserModel.username == username)
        model = self.db.scalar(statement)
        return model.to_domain() if model else None

    def get_by_id(self, user_id: UUID) -> User | None:
        model = self.db.get(UserModel, str(user_id))
        return model.to_domain() if model else None

    def list_all(self) -> list[User]:
        statement = select(UserModel).order_by(UserModel.full_name.asc())
        return [model.to_domain() for model in self.db.scalars(statement)]
