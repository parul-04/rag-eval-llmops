import time
import logging
from pydantic import BaseModel
from google import genai
from google.genai import types
from rag.config import settings

log = logging.getLogger(__name__)

# CHANGE 1: retry with exponential backoff on temporary server errors (503, 429, ...)
client = genai.Client(
    api_key=settings.GEMINI_API_KEY,
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(attempts=5, initial_delay=2.0, max_delay=30.0)
    ),
)


class LLMResult(BaseModel):
    text: str
    input_tokens: int
    output_tokens: int
    latency_s: float


def generate(prompt: str, *, system: str | None = None, temperature: float = 0.0,
             max_tokens: int = 1024, schema: type[BaseModel] | None = None) -> LLMResult:
    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=temperature,
        max_output_tokens=max_tokens,
        response_mime_type="application/json" if schema else None,
        response_schema=schema,
        # CHANGE 2: we pass no tools, so turn off automatic function calling
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    start = time.perf_counter()
    resp = client.models.generate_content(model=settings.LLM_MODEL, contents=prompt, config=config)
    latency = time.perf_counter() - start

    if not resp.text:
        raise RuntimeError(f"Empty response. Try raising max_tokens. Raw: {resp}")

    usage = resp.usage_metadata
    result = LLMResult(
        text=resp.text,
        input_tokens=usage.prompt_token_count or 0,
        output_tokens=usage.candidates_token_count or 0,
        latency_s=round(latency, 3),
    )
    log.info("model=%s in=%d out=%d latency=%.2fs", settings.LLM_MODEL,
             result.input_tokens, result.output_tokens, result.latency_s)
    return result