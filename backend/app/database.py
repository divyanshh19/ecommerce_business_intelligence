"""
Module: database.py
Purpose: Database connection management supporting both MySQL 8+ and SQLite fallback.
"""

import os
import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Determine Database URL
# Default is SQLite in data/olist_bi.db for zero-config immediate local execution,
# or can be overridden via DATABASE_URL environment variable for MySQL 8+
DEFAULT_SQLITE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "olist_bi.db"
DEFAULT_DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")

def get_engine(db_url: str = None):
    url = db_url or os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")
    connect_args = {}
    if "sqlite" in url:
        connect_args = {"check_same_thread": False}
    return create_engine(url, connect_args=connect_args, pool_pre_ping=True)

engine = get_engine(DEFAULT_DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI Dependency for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db(schema_file_path: str = None):
    """Execute DDL schema and view definitions."""
    if schema_file_path is None:
        schema_file_path = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"
    
    schema_path = Path(schema_file_path)
    if not schema_path.exists():
        logger.error(f"Schema file not found at {schema_path}")
        return False
        
    with open(schema_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split by semicolon for execution
    statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
    with engine.connect() as conn:
        for stmt in statements:
            try:
                # If running on SQLite, convert MySQL specific functions gracefully
                if "sqlite" in str(engine.url):
                    stmt_clean = stmt.replace("AUTO_INCREMENT", "")
                    stmt_clean = stmt_clean.replace("DATETIME DEFAULT CURRENT_TIMESTAMP", "DATETIME DEFAULT CURRENT_TIMESTAMP")
                else:
                    stmt_clean = stmt
                conn.execute(text(stmt_clean))
            except Exception as e:
                logger.warning(f"Note on DDL statement: {e}")
        conn.commit()
    logger.info("Database schema initialized successfully.")
    return True
