import logging
from pydantic import BaseModel
from rag.llm import generate

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class Answer(BaseModel):
    answer: str
    confidence: float


q = "In one sentence, what is a context window in an LLM?"

# Experiment 1: temperature. Is the output identical across runs?
for t in (0.0, 1.0):
    for run in range(2):
        r = generate(q, temperature=t)
        print(f"temp={t} run={run}: {r.text.strip()[:100]}")

# Experiment 2: structured output validated by Pydantic
r = generate(q, schema=Answer)
print(Answer.model_validate_json(r.text))