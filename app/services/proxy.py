from app.config import settings
from groq import AsyncGroq

groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)


async def forward_to_llm(sanitized_prompt: str) -> str:
    """Dispatches the clean, verified prompt to the downstream model."""
    try:
        response = await groq_client.chat.completions.create(
            model=settings.DOWNSTREAM_LLM_MODEL,
            messages=[{"role": "user", "content": sanitized_prompt}],
            temperature=0.7,
            timeout=20.0,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"[Gateway Error] Downstream model unreachable: {str(e)}"