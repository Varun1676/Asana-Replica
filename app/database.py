from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import QueuePool
import os

# Get DB URL from env or default to SQLite for local dev if not specified
# But adhering to user request for Postgres primarily
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./asana.db")

connect_args = {}
pool_config = {}

if "sqlite" in DATABASE_URL:
    # SQLite Setup (Single file, no pooling needed usually)
    connect_args = {"check_same_thread": False}
    # StaticPool is default for in-memory, but for file we use default.
else:
    # Postgres / General Production Setup (Connection Pooling)
    pool_config = {
        "pool_size": 20,         # Baseline number of connections to keep open
        "max_overflow": 10,      # Extra connections allowed during spikes
        "pool_timeout": 30,      # Wait 30s for a connection before failing
        "pool_recycle": 1800,    # Recycle connections every 30 mins to prevent stale errors
        "pool_pre_ping": True    # Check connection health before handing it out
    }

engine = create_engine(
    DATABASE_URL, 
    echo=False, # Verify query perf in prod by disabling echo
    connect_args=connect_args,
    **pool_config
)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)