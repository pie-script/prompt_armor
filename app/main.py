from datetime import datetime, timezone
import time
from typing import List, Optional
from app.config import settings
from app.models.database import AuditEvent
from app.models.schemas import (
    PromptRequest,
    PromptResponse,
    SecurityViolationDetail,
)
from app.security.heuristics import scan_heuristics
from app.security.llm_guard import evaluate_prompt_semantic
from app.security.pii_scrubber import scrub_sensitive_data
from app.services.audit import (
    AuditEventResponse,
    get_audit_logs,
    get_audit_stats,
    get_db,
    log_audit_event,
)
from app.services.proxy import forward_to_llm
from fastapi import Depends, FastAPI, HTTPException, Request, status
from sqlalchemy.orm import Session

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}


@app.post("/v1/chat", response_model=PromptResponse)
async def inspect_chat(
    payload: PromptRequest, raw_request: Request, db: Session = Depends(get_db)
):
    start_time = time.perf_counter()
    client_ip = raw_request.client.host if raw_request.client else "unknown"

    # ------------------------------------------------------------------
    # Layer 1: Heuristic Injection Scanner (Sub-ms drop)
    # ------------------------------------------------------------------
    heuristic_res = scan_heuristics(payload.prompt)
    if heuristic_res["is_threat"]:
        latency_ms = (time.perf_counter() - start_time) * 1000

        log_audit_event(
            raw_prompt=payload.prompt,
            sanitized_prompt="[BLOCKED]",
            decision="BLOCKED",
            threat_category=heuristic_res["threat_category"],
            confidence_score=heuristic_res["confidence_score"],
            rule_triggered=heuristic_res["rule_triggered"],
            latency_ms=round(latency_ms, 2),
            client_ip=client_ip,
            user_id=payload.user_id,
            db=db,
        )

        violation = SecurityViolationDetail(
            status="BLOCKED",
            threat_category=heuristic_res["threat_category"],
            rule_triggered=heuristic_res["rule_triggered"],
            confidence_score=heuristic_res["confidence_score"],
            timestamp=datetime.now(timezone.utc),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=violation.model_dump(mode="json"),
        )

    # ------------------------------------------------------------------
    # Layer 2: PII Redaction Engine
    # ------------------------------------------------------------------
    pii_res = scrub_sensitive_data(payload.prompt)
    sanitized_text = pii_res["sanitized_text"]
    has_pii = pii_res["total_replacements"] > 0

    threat_category = "OWASP_LLM02_LEAK" if has_pii else "NONE"
    rule_triggered = (
        ", ".join(pii_res["detected_entities"]) if has_pii else None
    )
    confidence_score = 1.0 if has_pii else 0.0

    # ------------------------------------------------------------------
    # Layer 3: Autonomous Semantic Judge (Groq Safeguard)
    # ------------------------------------------------------------------
    verdict = await evaluate_prompt_semantic(sanitized_text)
    if verdict.is_jailbreak:
        latency_ms = (time.perf_counter() - start_time) * 1000

        log_audit_event(
            raw_prompt=payload.prompt,
            sanitized_prompt=sanitized_text,
            decision="BLOCKED",
            threat_category=verdict.risk_category,
            confidence_score=verdict.risk_score,
            rule_triggered=verdict.reasoning,
            latency_ms=round(latency_ms, 2),
            client_ip=client_ip,
            user_id=payload.user_id,
            db=db,
        )

        violation = SecurityViolationDetail(
            status="BLOCKED",
            threat_category=verdict.risk_category,
            rule_triggered=verdict.reasoning,
            confidence_score=verdict.risk_score,
            timestamp=datetime.now(timezone.utc),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=violation.model_dump(mode="json"),
        )

    # ------------------------------------------------------------------
    # Downstream Dispatcher (Pass clean prompt to target LLM)
    # ------------------------------------------------------------------
    llm_output = await forward_to_llm(sanitized_text)
    latency_ms = (time.perf_counter() - start_time) * 1000

    # ------------------------------------------------------------------
    # Record Safe / Allowed Event
    # ------------------------------------------------------------------
    log_audit_event(
        raw_prompt=payload.prompt,
        sanitized_prompt=sanitized_text,
        decision="ALLOWED",
        threat_category=threat_category,
        confidence_score=confidence_score,
        rule_triggered=rule_triggered,
        latency_ms=round(latency_ms, 2),
        client_ip=client_ip,
        user_id=payload.user_id,
        db=db,
    )

    return PromptResponse(
        status="ALLOWED",
        sanitized_prompt=sanitized_text,
        latency_ms=round(latency_ms, 2),
        model_response=llm_output,
    )


@app.get("/v1/audit/logs", response_model=List[AuditEventResponse])
def list_events(
    skip: int = 0,
    limit: int = 50,
    decision: Optional[str] = None,
    db: Session = Depends(get_db),
):
    logs = get_audit_logs(db=db, skip=skip, limit=limit, decision=decision)
    return logs


@app.get("/v1/audit/stats")
def audit_stats(db: Session = Depends(get_db)):
    return get_audit_stats(db)