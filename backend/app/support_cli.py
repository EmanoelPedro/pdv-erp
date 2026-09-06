import argparse
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import create_engine, delete, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.database.models import UserModel, UserSessionModel
from app.services.security import hash_pin

DEFAULT_DESKTOP_DATA_DIR = Path.home() / ".local" / "share" / "com.pdv.local"


def resolve_data_dir(data_dir_argument: str | None) -> Path | None:
    if data_dir_argument:
        return Path(data_dir_argument).expanduser().resolve()

    settings = get_settings()
    if settings.resolved_data_dir is not None:
        return settings.resolved_data_dir

    if DEFAULT_DESKTOP_DATA_DIR.exists():
        return DEFAULT_DESKTOP_DATA_DIR

    return None


def resolve_database_url(data_dir_argument: str | None) -> str:
    settings = get_settings()
    resolved_data_dir = resolve_data_dir(data_dir_argument)

    if resolved_data_dir is None or settings.database_url != "sqlite:///./pdv.db":
        return settings.resolved_database_url

    return f"sqlite:///{(resolved_data_dir / 'pdv.db').as_posix()}"


def resolve_database_path(data_dir_argument: str | None) -> Path | None:
    database_url = resolve_database_url(data_dir_argument)
    if not database_url.startswith("sqlite:///"):
        return None

    parsed = urlparse(database_url)
    return Path(parsed.path).resolve()


def print_runtime_info(data_dir_argument: str | None) -> None:
    print(f"data_dir: {resolve_data_dir(data_dir_argument)}")
    print(f"database_url: {resolve_database_url(data_dir_argument)}")

    database_path = resolve_database_path(data_dir_argument)
    if database_path is not None:
        print(f"database_path: {database_path}")


def create_session_factory(data_dir_argument: str | None) -> sessionmaker[Session]:
    database_url = resolve_database_url(data_dir_argument)
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
    )
    return sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


def normalize_username(username: str) -> str:
    return username.strip().lower()


def get_user_by_username(db: Session, username: str) -> UserModel:
    normalized_username = normalize_username(username)
    statement = select(UserModel).where(UserModel.username == normalized_username)
    user = db.scalar(statement)
    if user is None:
        raise SystemExit(f"User '{normalized_username}' was not found.")

    return user


def list_users(_: argparse.Namespace) -> int:
    print_runtime_info(_.data_dir)
    session_factory = create_session_factory(_.data_dir)

    with session_factory() as db:
        users = list(db.scalars(select(UserModel).order_by(UserModel.created_at.asc())))
        session_count = db.scalar(select(func.count()).select_from(UserSessionModel))

        print(f"users: {len(users)}")
        print(f"sessions: {int(session_count or 0)}")

        if not users:
            return 0

        for user in users:
            print(
                " | ".join(
                    [
                        f"id={user.id}",
                        f"username={user.username}",
                        f"name={user.full_name}",
                        f"role={user.role}",
                        f"active={user.is_active}",
                        f"created_at={user.created_at}",
                    ]
                )
            )

    return 0


def set_username(args: argparse.Namespace) -> int:
    current_username = normalize_username(args.current_username)
    new_username = normalize_username(args.new_username)
    session_factory = create_session_factory(args.data_dir)

    with session_factory() as db:
        user = get_user_by_username(db, current_username)
        existing_user = db.scalar(select(UserModel).where(UserModel.username == new_username))
        if existing_user is not None and existing_user.id != user.id:
            raise SystemExit(f"Username '{new_username}' is already in use.")

        user.username = new_username
        db.commit()

        print(f"Updated username: {current_username} -> {new_username}")

    return 0


def revoke_sessions_for_user(db: Session, user_id: str) -> int:
    result = db.execute(delete(UserSessionModel).where(UserSessionModel.user_id == user_id))
    return int(result.rowcount or 0)


def set_pin(args: argparse.Namespace) -> int:
    username = normalize_username(args.username)
    session_factory = create_session_factory(args.data_dir)

    with session_factory() as db:
        user = get_user_by_username(db, username)
        user.pin_hash = hash_pin(args.pin)
        revoked_sessions = revoke_sessions_for_user(db, user.id)
        db.commit()

        print(f"Updated PIN for user '{username}'.")
        print(f"Revoked sessions: {revoked_sessions}")

    return 0


def set_active_state(args: argparse.Namespace, is_active: bool) -> int:
    username = normalize_username(args.username)
    session_factory = create_session_factory(args.data_dir)

    with session_factory() as db:
        user = get_user_by_username(db, username)
        user.is_active = is_active

        revoked_sessions = 0
        if not is_active:
            revoked_sessions = revoke_sessions_for_user(db, user.id)

        db.commit()

        state_label = "activated" if is_active else "deactivated"
        print(f"User '{username}' {state_label}.")
        if not is_active:
            print(f"Revoked sessions: {revoked_sessions}")

    return 0


def activate_user(args: argparse.Namespace) -> int:
    return set_active_state(args, True)


def deactivate_user(args: argparse.Namespace) -> int:
    return set_active_state(args, False)


def clear_sessions(args: argparse.Namespace) -> int:
    session_factory = create_session_factory(args.data_dir)

    with session_factory() as db:
        if args.username:
            user = get_user_by_username(db, args.username)
            deleted_sessions = revoke_sessions_for_user(db, user.id)
            label = f"user '{normalize_username(args.username)}'"
        else:
            result = db.execute(delete(UserSessionModel))
            deleted_sessions = int(result.rowcount or 0)
            label = "all users"

        db.commit()

        print(f"Cleared sessions for {label}: {deleted_sessions}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Support tools for the local PDV desktop database."
    )
    parser.add_argument(
        "--data-dir",
        help=(
            "Override the application data directory. "
            "Defaults to the desktop app data path when available."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_users_parser = subparsers.add_parser(
        "list-users", help="Show local users and session count."
    )
    list_users_parser.set_defaults(handler=list_users)

    set_username_parser = subparsers.add_parser("set-username", help="Rename a local username.")
    set_username_parser.add_argument("--current-username", required=True)
    set_username_parser.add_argument("--new-username", required=True)
    set_username_parser.set_defaults(handler=set_username)

    set_pin_parser = subparsers.add_parser("set-pin", help="Reset the PIN for a local user.")
    set_pin_parser.add_argument("--username", required=True)
    set_pin_parser.add_argument("--pin", required=True)
    set_pin_parser.set_defaults(handler=set_pin)

    activate_user_parser = subparsers.add_parser("activate-user", help="Activate a local user.")
    activate_user_parser.add_argument("--username", required=True)
    activate_user_parser.set_defaults(handler=activate_user)

    deactivate_user_parser = subparsers.add_parser(
        "deactivate-user", help="Deactivate a local user."
    )
    deactivate_user_parser.add_argument("--username", required=True)
    deactivate_user_parser.set_defaults(handler=deactivate_user)

    clear_sessions_parser = subparsers.add_parser(
        "clear-sessions", help="Revoke saved login sessions."
    )
    clear_sessions_parser.add_argument("--username")
    clear_sessions_parser.set_defaults(handler=clear_sessions)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
