from app.models.database import SessionLocal, AuditEvent
from sqlalchemy.orm import Session

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


    