import json
from decimal import Decimal

from sqlalchemy.orm import Session

from app.domain.sync_queue import SyncStatus
from app.repositories.sync_queue_repository import SyncQueueRepository
from app.services.sync_queue_service import SyncQueueService


def test_enqueue_event_persists_serialized_payload(db_session: Session) -> None:
    service = SyncQueueService(SyncQueueRepository(db_session))

    entry = service.enqueue_event(
        entity_type="sale",
        entity_id="sale-123",
        event_type="sale_completed",
        payload={
            "saleId": "sale-123",
            "totalAmount": Decimal("42.50"),
            "items": [{"productId": "prod-1", "quantity": 2}],
        },
    )

    assert entry.entity_type == "SALE"
    assert entry.event_type == "SALE_COMPLETED"
    assert entry.sync_status == SyncStatus.PENDING
    assert json.loads(entry.payload) == {
        "items": [{"productId": "prod-1", "quantity": 2}],
        "saleId": "sale-123",
        "totalAmount": "42.50",
    }
    assert service.list_pending() == [entry]


def test_mark_failed_increments_retry_count(db_session: Session) -> None:
    service = SyncQueueService(SyncQueueRepository(db_session))
    entry = service.enqueue_event(
        entity_type="expense",
        entity_id="expense-1",
        event_type="expense_created",
        payload={"expenseId": "expense-1"},
    )

    failed_entry = service.mark_failed(entry.id, "Cloud API unavailable")

    assert failed_entry.sync_status == SyncStatus.FAILED
    assert failed_entry.retry_count == 1
    assert failed_entry.last_error == "Cloud API unavailable"
    assert service.list_pending() == []


def test_mark_synced_removes_entry_from_pending_queue(db_session: Session) -> None:
    service = SyncQueueService(SyncQueueRepository(db_session))
    entry = service.enqueue_event(
        entity_type="cash_register_session",
        entity_id="session-1",
        event_type="cash_register_closed",
        payload={"sessionId": "session-1"},
    )

    synced_entry = service.mark_synced(entry.id)

    assert synced_entry.sync_status == SyncStatus.SYNCED
    assert synced_entry.retry_count == 0
    assert synced_entry.last_error is None
    assert service.list_pending() == []
