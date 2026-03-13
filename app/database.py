import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("database_manager")

# Use DATABASE_URL env var if set (e.g. Railway PostgreSQL plugin),
# otherwise fall back to a local SQLite file.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///aqi_dashboard.db")

# SQLAlchemy 1.4+ requires "postgresql://" not "postgres://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    with engine.connect() as conn:
        safe_url = (
            DATABASE_URL.split("@")[-1]
            if "@" in DATABASE_URL
            else DATABASE_URL
        )
        logger.info(f"Connected to database: {safe_url}")
except Exception as err:
    logger.error(f"Failed to connect to database: {err}")
    # Fallback to in-memory SQLite so the app can boot for diagnostics
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )

session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(session_factory)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
