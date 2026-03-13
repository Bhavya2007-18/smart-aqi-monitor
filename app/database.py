import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("database_manager")

# 1. Load DATABASE_URL from environment with fallback
# On Vercel, if no DB is provided, we use an in-memory sqlite to prevent read-only filesystem crashes
default_db = "sqlite:///:memory:" if os.environ.get("VERCEL") else "sqlite:///aqi_dashboard.db"
DATABASE_URL = os.getenv("DATABASE_URL", default_db)

# 3. Ensure compatibility with SQLAlchemy 1.4+ for postgres:// prefix (often used by Heroku/Supabase/Neon)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 4. Engine configuration
connect_args = {}
# For SQLite, check_same_thread is required. 
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# Use NullPool for Serverless (Vercel) to prevent connection pool exhaustion on cloud databases
is_serverless = bool(os.environ.get("VERCEL"))
# 4. & 6. Update engine creation logic for async-safe serverless execution
poolclass = NullPool if is_serverless or "postgresql" in DATABASE_URL else None

try:
    if poolclass:
        engine = create_engine(DATABASE_URL, connect_args=connect_args, poolclass=poolclass)
    else:
        engine = create_engine(DATABASE_URL, connect_args=connect_args)
    
    # 9. & 10. Add error handling and Log connection success or failure
    with engine.connect() as conn:
        # Avoid logging credentials
        safe_url = DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else (DATABASE_URL if DATABASE_URL.startswith("sqlite") else "PostgreSQL Server")
        logger.info(f"Successfully connected to the database at {safe_url}")
except Exception as err:
    logger.error(f"Failed to connect to the database: {str(err)}")
    # We create a dummy engine to allow the app to boot, though it will fail on DB queries
    # This helps diagnose if the crash is at the import level
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

# 6. Update session creation logic for async-safe serverless execution
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(session_factory)

Base = declarative_base()

# 7. Add automatic table creation on application startup if tables do not exist
def init_db():
    try:
        import app.models # Ensure models are loaded
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables automatically verified and created if missing.")
    except Exception as e:
        logger.error(f"Failed to auto-create tables: {str(e)}")

# Trigger automatic table creation on startup
init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

