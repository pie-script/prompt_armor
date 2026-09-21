from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Client Inbound Payload
class PromptRequest(BaseModel):
    prompt : str =Field(..., min_length=1, max_length=4000, description="Raw input prompt to inspect")
    user_id :Optional[str]=None
    session_id :Optional[str]=None
    

class SecurityViolationDetail(BaseModel):
    status :str="BLOCKED" # default blocked
    threat_category :str # eg "OWASP_LLM01_INJECTION", "OWASP_LLM02_LEAK")
    rule_triggered : str
    confidence_score : float
    timestamp :datetime
    
class PromptResponse(BaseModel):
    status :str = "ALLOWED" # ALLOWED/BLOCKED by deafult allowed
    sanitized_prompt : str
    latency_ms :float
    model_response : Optional[str] =None
    
    
    