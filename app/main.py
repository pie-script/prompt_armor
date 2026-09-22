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