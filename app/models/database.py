from sqlalchemy import create_engine,Column,Integer,String,DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL="sqlite:///security_logs.db"

engine=create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread":False}
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base=declarative_base()

class AuditEvent(Base):
    __tablename__="audit_events"
    id=Column(Integer,primary_key=True,autoincrement=True)
    timestamp=Column(DateTime,default=datetime.utcnow,index=True)
    
    client_ip=Column(String, nullable=True)
    user_id=Column(String, nullable=True)
    
    raw_prompt=Column(String, nullable=False)
    sanitized_prompt=Column(String, nullable=False)
    
    decision=Column(String,index=True,nullable=False)
    threat_category=Column(String,index=True,default="None")
    
    confidence_score=Column(Float,default=0.0)
    rule_triggered=Column(Float,nullable=True)
    latency_ms=Column(Float,nullable=False)
