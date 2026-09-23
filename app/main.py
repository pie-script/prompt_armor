from fastapi import FastAPI, status, HTTPException, Depends
import time
from app.config import settings
from app.models.schemas import PromptRequest,PromptResponse
from sqlalchemy.orm import Session
from typing import List,Optional
from app.models.database import AuditEvent
from app.services.audit import AuditEventResponse,get_db,get_audit_logs,get_audit_stats

app=FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service":settings.APP_NAME}

@app.post("/v1/chat",response_model=PromptResponse)
async def inspect_chat(request:PromptRequest):
    start_time=time.perf_counter()
    latency_ms = (time.perf_counter() -start_time)*1000
    return PromptResponse(
        status="ALLOWED",
        sanitized_prompt=request.prompt,
        latency_ms=round(latency_ms,2),
        model_response=None
    )
    
@app.get('/v1/audit/logs',response_model =List[AuditEventResponse])
def lists_events(
    skip :int=0,
    limit: int =50,
    decision: Optional[str]=None,
    db:Session=Depends(get_db)
):
    logs=get_audit_logs(
        db=db,
        skip=skip,
        limit=limit,
        decision=decision
    )
    return logs
    
@app.get("/v1/audit/stats")
def audit_stats(db:Session=Depends(get_db)):
    return get_audit_stats(db)