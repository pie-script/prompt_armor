from fastapi import FastAPI, status, HTTPException
import time
from app.config import settings
from app.models.schemas import PromptRequest,PromptResponse

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
    

