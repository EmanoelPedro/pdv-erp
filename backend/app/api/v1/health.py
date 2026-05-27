from fastapi import APIRouter, HTTPException

from app.local_runtime import get_runtime_readiness

root_health_router = APIRouter(tags=["health"])
router = APIRouter(tags=["health"])


@root_health_router.get("/health")
def root_healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": "pdv-backend"}


@root_health_router.get("/health/ready")
def root_readiness_check() -> dict[str, str]:
    try:
        readiness = get_runtime_readiness()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "status": "ok",
        "service": "pdv-backend",
        "database": readiness["database"],
        "migrations": readiness["migrations"],
    }


@router.get("/health")
def versioned_healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": "pdv-backend", "version": "v1"}


@router.get("/health/ready")
def versioned_readiness_check() -> dict[str, str]:
    try:
        readiness = get_runtime_readiness()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "status": "ok",
        "service": "pdv-backend",
        "version": "v1",
        "database": readiness["database"],
        "migrations": readiness["migrations"],
    }
