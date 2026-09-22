from fastapi import FastAPI, status, HTTPException
import time
from app.config import settings
from app.models.schemas import PromptRequest,PromptResponse

app=FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)