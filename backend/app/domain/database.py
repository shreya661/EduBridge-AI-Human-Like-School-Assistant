"""Database connection and session management for PostgreSQL / SQLite."""

import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.domain.sql_models import Base

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
SessionLocal = None

if DATABASE_URL:
    # Normalize postgres:// to postgresql:// for SQLAlchemy 2.0
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
    engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)


def get_db_session() -> Optional[Session]:
    """Get a fresh database session if DATABASE_URL is configured."""
    if SessionLocal:
        return SessionLocal()
    return None
