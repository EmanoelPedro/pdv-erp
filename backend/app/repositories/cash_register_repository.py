from datetime import UTC, date, datetime, time, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import CashRegisterSessionModel
from app.domain.cash_register import CashRegisterSession, CashRegisterStatus
from app.domain.exceptions import CashRegisterNotFoundError


class CashRegisterSessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, session: CashRegisterSession) -> CashRegisterSession:
        model = CashRegisterSessionModel.from_domain(session)
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return model.to_domain()

    def get_open_session(self) -> CashRegisterSession | None:
        statement = select(CashRegisterSessionModel).where(
            CashRegisterSessionModel.status == CashRegisterStatus.OPEN.value,
        )
        model = self.db.scalar(statement)
        return model.to_domain() if model else None

    def get_by_id(self, session_id: UUID) -> CashRegisterSession | None:
        model = self.db.get(CashRegisterSessionModel, str(session_id))
        return model.to_domain() if model else None

    def list_all(
        self,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[CashRegisterSession]:
        statement = select(CashRegisterSessionModel).order_by(
            CashRegisterSessionModel.opened_at.desc(),
        )

        if start_date is not None:
            opened_from = datetime.combine(start_date, time.min, tzinfo=UTC)
            statement = statement.where(CashRegisterSessionModel.opened_at >= opened_from)

        if end_date is not None:
            opened_to = datetime.combine(end_date + timedelta(days=1), time.min, tzinfo=UTC)
            statement = statement.where(CashRegisterSessionModel.opened_at < opened_to)

        return [model.to_domain() for model in self.db.scalars(statement)]

    def update(self, session: CashRegisterSession) -> CashRegisterSession:
        model = self.db.get(CashRegisterSessionModel, str(session.id))
        if model is None:
            raise CashRegisterNotFoundError("Cash register session was not found.")

        model.update_from_domain(session)
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return model.to_domain()
