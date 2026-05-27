from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import SyncQueueEntryModel
from app.domain.sync_queue import SyncQueueEntry, SyncStatus


class SyncQueueRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, entry: SyncQueueEntry) -> SyncQueueEntry:
        model = SyncQueueEntryModel.from_domain(entry)
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return model.to_domain()

    def get_by_id(self, entry_id: UUID) -> SyncQueueEntry | None:
        model = self.db.get(SyncQueueEntryModel, str(entry_id))
        return model.to_domain() if model else None

    def list_by_status(
        self,
        status: SyncStatus,
        *,
        limit: int = 100,
    ) -> list[SyncQueueEntry]:
        statement = (
            select(SyncQueueEntryModel)
            .where(SyncQueueEntryModel.sync_status == status.value)
            .order_by(SyncQueueEntryModel.created_at.asc())
            .limit(limit)
        )

        return [model.to_domain() for model in self.db.scalars(statement)]

    def update(self, entry: SyncQueueEntry) -> SyncQueueEntry:
        model = self.db.get(SyncQueueEntryModel, str(entry.id))
        if model is None:
            msg = "Sync queue entry was not found."
            raise LookupError(msg)

        model.update_from_domain(entry)
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return model.to_domain()
