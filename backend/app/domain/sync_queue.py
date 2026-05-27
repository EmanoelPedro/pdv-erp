from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.shared import ensure_utc, utc_now


class SyncStatus(StrEnum):
    PENDING = "PENDING"
    SYNCED = "SYNCED"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class SyncQueueEntry:
    id: UUID
    entity_type: str
    entity_id: str
    event_type: str
    payload: str
    sync_status: SyncStatus
    retry_count: int
    created_at: datetime
    updated_at: datetime
    last_error: str | None

    @classmethod
    def enqueue(
        cls,
        *,
        entity_type: str,
        entity_id: str,
        event_type: str,
        payload: str,
        created_at: datetime | None = None,
    ) -> "SyncQueueEntry":
        timestamp = ensure_utc(created_at or utc_now())

        return cls(
            id=uuid4(),
            entity_type=entity_type.strip().upper(),
            entity_id=entity_id.strip(),
            event_type=event_type.strip().upper(),
            payload=payload,
            sync_status=SyncStatus.PENDING,
            retry_count=0,
            created_at=timestamp,
            updated_at=timestamp,
            last_error=None,
        )

    def mark_synced(self, *, processed_at: datetime | None = None) -> "SyncQueueEntry":
        timestamp = ensure_utc(processed_at or utc_now())
        return replace(
            self,
            sync_status=SyncStatus.SYNCED,
            updated_at=timestamp,
            last_error=None,
        )

    def mark_failed(
        self,
        error_message: str | None,
        *,
        failed_at: datetime | None = None,
    ) -> "SyncQueueEntry":
        timestamp = ensure_utc(failed_at or utc_now())
        return replace(
            self,
            sync_status=SyncStatus.FAILED,
            retry_count=self.retry_count + 1,
            updated_at=timestamp,
            last_error=error_message.strip() or None if error_message else None,
        )
