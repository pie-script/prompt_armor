# SQLAlchemy imports: engine, column types, and ORM tools 
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# 1. DATABASE URL 
# Points SQLite to the data/ folder at project root
DATABASE_URL = "sqlite:///./data/security_logs.db"

# 2. ENGINE 
# create_engine sets up the connection to the SQLite file.
# check_same_thread=False is required for FastAPI's async/multi-threaded environment.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 3. SESSION FACTORY 
# SessionLocal is used to open/close DB sessions per request.
# autocommit=False → we control when changes are committed.
# autoflush=False  → prevents automatic DB writes before commit.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 4. BASE CLASS 
# All ORM models inherit from Base so SQLAlchemy can track them.
Base = declarative_base()


# 5. AUDIT EVENT MODEL 
class AuditEvent(Base):
    """Relational model for every prompt inspection event logged by the gateway."""
    __tablename__ = "audit_events"

    # Primary key — auto-increments with each new record
    id        = Column(Integer, primary_key=True, autoincrement=True)

    # When the event was recorded — indexed for fast time-range queries
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Source identity (both nullable — not always available)
    client_ip = Column(String, nullable=True)   # IP address of the caller
    user_id   = Column(String, nullable=True)   # User ID from the request payload

    # Prompt content
    raw_prompt       = Column(Text, nullable=False)  # Original unaltered prompt
    sanitized_prompt = Column(Text, nullable=False)  # Prompt after PII/injection masking

    # Security verdict — indexed for fast filtering in audit queries
    decision         = Column(String, index=True, nullable=False)          # "ALLOWED" or "BLOCKED"
    threat_category  = Column(String, index=True, default="NONE")          # e.g. "OWASP_LLM01_INJECTION"

    # Threat scoring
    confidence_score = Column(Float, default=0.0)    # 0.0 (clean) → 1.0 (certain threat)
    rule_triggered   = Column(String, nullable=True) # Rule/signature name that fired

    # Performance tracking
    latency_ms = Column(Float, nullable=False)  # Total inspection time in milliseconds


# 6. TABLE INITIALIZER 
def init_db():
    """Create all tables defined via Base if they don't already exist.
    Safe to call on every startup — skips existing tables."""
    Base.metadata.create_all(bind=engine)