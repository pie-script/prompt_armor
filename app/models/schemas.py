from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Client Inbound Payload
class PromptRequest(BaseModel):
    prompt : str =Field(..., min_length=1, max_length=4000, description="Raw input prompt to inspect")
    user_id :Optional[str]=None
    session_id :Optional[str]=None
    


