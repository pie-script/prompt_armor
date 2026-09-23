from app.models.database import SessionLocal, AuditEvent
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class AuditEventResponse(BaseModel):
    id:int
    timestamp:datetime
    client_ip:Optional[str]
    user_id:Optional[str]
    raw_prompt:str
    sanitized_prompt:str
    decision:str
    threat_category:str
    confidence_score:float
    rule_triggered:Optional[str]
    latency_ms:float
    model_config={"from_attributes":True}

def get_db() :

    db=SessionLocal()
    try :
        yield db
    finally:
        db.close()

def log_audit_event(
    raw_prompt:str,
    sanitized_prompt:str,
    decision:str,
    threat_category:str,
    confidence_score:float,
    rule_triggered:str,
    latency_ms:float,
    client_ip:str=None,
    user_id:str=None,
    db: Session =None
):
    owns_session=db is None
    if owns_session:
        db=SessionLocal()
    try:
        event=AuditEvent(
            raw_prompt=raw_prompt,
            sanitized_prompt=sanitized_prompt,
            decision=decision,
            threat_category=threat_category,
            confidence_score=confidence_score,
            rule_triggered=rule_triggered,
            latency_ms=latency_ms,
            client_ip=client_ip,
            user_id=user_id
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    except Exception as e:
    
        db.rollback()
        raise e

    finally:
        if owns_session:
            db.close()

def get_audit_logs(
    db:Session,
    skip : int=0,
    limit: int=50,
    decision: Optional[str] =None
):
    query=db.query(AuditEvent)
    if decision:
        query=query.filter(AuditEvent.decision==decision)
    logs=query.order_by(AuditEvent.timestamp.desc()).offset(skip).limit(limit).all()
    return logs

def get_audit_stats(db: Session):
    total=db.query(AuditEvent).count()
    blocked=db.query(AuditEvent).filter(AuditEvent.decision=="BLOCKED").count()
    allowed=total-blocked
    return {
        "total_prompts":total,
        "allowed_prompts":allowed,
        "blocked_prompts":blocked
    } 

