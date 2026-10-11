"""Backend-only SQLite models and connection setup."""

import os
from pathlib import Path

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, create_engine, event, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

DATABASE_FILE = Path(__file__).resolve().parents[2] / "mail.db"


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email_address: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(Text)
    history_id: Mapped[str | None] = mapped_column(String)
    messages: Mapped[list["CachedMessage"]] = relationship(cascade="all, delete-orphan")
    pages: Mapped[list["CachedPage"]] = relationship(cascade="all, delete-orphan")


class CachedMessage(Base):
    __tablename__ = "cached_messages"

    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True)
    gmail_id: Mapped[str] = mapped_column(String, primary_key=True)
    thread_id: Mapped[str] = mapped_column(String, nullable=False)
    sender: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    snippet: Mapped[str] = mapped_column(Text, nullable=False)
    received_at: Mapped[str] = mapped_column(String, nullable=False)
    starred: Mapped[bool] = mapped_column(Boolean, nullable=False)
    label_ids_json: Mapped[str] = mapped_column(Text, nullable=False)


class CachedPage(Base):
    __tablename__ = "cached_pages"

    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True)
    cache_key: Mapped[str] = mapped_column(Text, primary_key=True)
    message_ids_json: Mapped[str] = mapped_column(Text, nullable=False)
    labels_json: Mapped[str] = mapped_column(Text, nullable=False)
    next_page_token: Mapped[str | None] = mapped_column(Text)


engine = create_engine(f"sqlite:///{DATABASE_FILE}", connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def configure_connection(connection, _record) -> None:
    connection.execute("PRAGMA foreign_keys=ON")


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def initialize_database() -> None:
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATABASE_FILE.exists():
        DATABASE_FILE.touch(mode=0o600)
    try:
        os.chmod(DATABASE_FILE, 0o600)
    except OSError:
        pass
    Base.metadata.create_all(engine)
    if "accounts" in inspect(engine).get_table_names() and "history_id" not in {
        column["name"] for column in inspect(engine).get_columns("accounts")
    }:
        with engine.begin() as connection:
            connection.exec_driver_sql("ALTER TABLE accounts ADD COLUMN history_id VARCHAR")
