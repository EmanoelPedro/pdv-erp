import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from app.domain.sync_queue import SyncQueueEntry, SyncStatus
from app.repositories.sync_queue_repository import SyncQueueRepository


def _json_default(value: object) -> str | dict[str, object]:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return str(value.value)
    if is_dataclass(value):
        return asdict(value)

    msg = f"Object of type {type(value).__name__} is not JSON serializable"
    raise TypeError(msg)


class SyncQueueService:
    def __init__(self, repository: SyncQueueRepository) -> None:
        self.repository = repository

    def enqueue_event(
        self,
        *,
        entity_type: str,
        entity_id: str,
        event_type: str,
        payload: object,
    ) -> SyncQueueEntry:
        serialized_payload = json.dumps(
            payload,
            default=_json_default,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        entry = SyncQueueEntry.enqueue(
            entity_type=entity_type,
            entity_id=entity_id,
            event_type=event_type,
            payload=serialized_payload,
        )

        try:
            created_entry = self.repository.create(entry)
            self.repository.db.commit()
            return created_entry
        except Exception:
            self.repository.db.rollback()
            raise

    def list_pending(self, *, limit: int = 100) -> list[SyncQueueEntry]:
        return self.repository.list_by_status(SyncStatus.PENDING, limit=limit)

    def mark_synced(self, entry_id: UUID) -> SyncQueueEntry:
        entry = self.repository.get_by_id(entry_id)
        if entry is None:
            msg = "Sync queue entry was not found."
            raise LookupError(msg)

        try:
            updated_entry = self.repository.update(entry.mark_synced())
            self.repository.db.commit()
            return updated_entry
        except Exception:
            self.repository.db.rollback()
            raise

    def mark_failed(self, entry_id: UUID, error_message: str | None) -> SyncQueueEntry:
        entry = self.repository.get_by_id(entry_id)
        if entry is None:
            msg = "Sync queue entry was not found."
            raise LookupError(msg)

        try:
            updated_entry = self.repository.update(entry.mark_failed(error_message))
            self.repository.db.commit()
            return updated_entry
        except Exception:
            self.repository.db.rollback()
            raise
