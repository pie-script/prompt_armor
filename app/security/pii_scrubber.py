import re

TARGET_PATTERNS=[
    
    # API Keys & Tokens (supports sk-live-, sk-proj-, etc.)
    ("OPENAI_KEY",   re.compile(r'\bsk-[a-zA-Z0-9_\-]{20,}\b')),
    ("AWS_KEY",      re.compile(r'\bAKIA[0-9A-Z]{16}\b')),
    ("GOOGLE_KEY",   re.compile(r'\bAIza[0-9A-Za-z\-_]{35}\b')),
    ("BEARER_TOKEN", re.compile(r'\bBearer\s+[a-zA-Z0-9_\-\.]{20,}\b')),

    # PII & Sensitive Identifiers
    ("EMAIL",        re.compile(r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b')),
    ("SSN",          re.compile(r'\b\d{3}-\d{2}-\d{4}\b')),
    ("PHONE_NUMBERS",re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?(?:\d{3}[-.\s]?)?\d{4}\b')),
    ("CREDIT_CARD",  re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')),
    ("SENSITIVE_IP", re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')),
    
]

def scrub_sensitive_data(text:str) -> dict :
    sanitized=text
    detected_labels=set()
    total_replacements=0

    for label, pattern in TARGET_PATTERNS:
        sanitized,count=pattern.subn(f'[REDACTED_{label}]',sanitized)

        if count>0:
            detected_labels.add(label)
            total_replacements+=count

    return {
        "sanitized_text":sanitized,
        "detected_entities":list(detected_labels),
        "total_replacements":total_replacements
    }

