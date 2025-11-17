"""
db_session.py
-------------

Database connection management using SQLAlchemy with PostgreSQL (Supabase).
Provides database session management for FastAPI dependency injection.

Responsibilities:
- Configure PostgreSQL connection engine
- Create SessionLocal for database sessions
- Provide get_db() function for FastAPI dependency injection
- Ensure proper connection opening/closing

"""


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os

# Build PostgreSQL connection URL from Supabase settings
# Format: postgresql://user:password@host:port/database
# Supabase URL format: https://PROJECT_REF.supabase.co
# Database host: db.PROJECT_REF.supabase.co


def get_database_url() -> str:
    """
    Construct PostgreSQL connection URL from environment variables.
    Extracts database credentials from Supabase configuration.
    """
    supabase_url = settings.SUPABASE_URL
    
    # Extract project reference from Supabase URL
    # Format: https://hhzrfesjunkbgxjkkpol.supabase.co
    project_ref = supabase_url.replace("https://", "").replace(
        ".supabase.co", ""
    )
    
    # Get database credentials from environment
    db_password = os.getenv("SUPABASE_SENHA", "")
    db_user = "postgres"
    db_name = "postgres"
    db_host = f"db.{project_ref}.supabase.co"
    db_port = "5432"
    
    # Build PostgreSQL connection URL
    database_url = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    
    return database_url


# Create SQLAlchemy engine
SQLALCHEMY_DATABASE_URL = get_database_url()
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Test connections before using them
    pool_size=10,  # Connection pool size
    max_overflow=20  # Max connections above pool_size
)

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session.
    Automatically handles session lifecycle (open/close).
    
    Usage in routers:
        @router.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db session here
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all tables defined in models.
    Should be called on application startup if needed.
    Note: Use Alembic for production migrations.
    """
    Base.metadata.create_all(bind=engine)

